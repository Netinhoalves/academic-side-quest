from collections import defaultdict
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, contains_eager

from app import models, schemas
from app.auth import get_current_aluno, get_current_validador
from app.database import get_db
from app.security import hash_password
from app.solicitacoes import aluno_do_usuario, montar_solicitacao

router = APIRouter(tags=["Alunos"])

@router.post("/auth/cadastro-aluno", response_model=schemas.AlunoCadastrado, status_code=status.HTTP_201_CREATED)
def create_aluno(dados: schemas.CadastroAluno, db: Session = Depends(get_db)):
    """Cadastra um aluno com perfil Aluno vinculado a um PPC ativo (Rota pública)."""
    if db.query(models.Usuario).filter(models.Usuario.email == dados.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail já cadastrado")

    if db.query(models.Usuario).filter(models.Usuario.matricula == dados.matricula).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Matrícula já cadastrada")

    ppc = db.query(models.PPC).filter(models.PPC.id == dados.id_ppc).first()
    if not ppc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="PPC não encontrado")
    if not ppc.ativo or not ppc.curso.ativo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="PPC inativo")

    perfil_aluno = db.query(models.Perfil).filter(models.Perfil.nome_perfil == "Aluno").first()
    if not perfil_aluno:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Perfil Aluno não configurado")

    usuario = models.Usuario(
        nome=dados.nome,
        email=dados.email,
        senha_hash=hash_password(dados.senha),
        matricula=dados.matricula,
        id_perfil=perfil_aluno.id,
        ativo=True,
    )

    try:
        db.add(usuario)
        db.flush()
        aluno = models.Aluno(
            id_usuario=usuario.id,
            id_ppc=ppc.id,
            data_ingresso=dados.data_ingresso or date.today(),
            status="ATIVO",
        )
        db.add(aluno)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail ou matrícula já cadastrados")

    db.refresh(usuario)
    db.refresh(aluno)
    return schemas.AlunoCadastrado(
        id_usuario=usuario.id,
        id_aluno=aluno.id,
        nome=usuario.nome,
        email=usuario.email,
        matricula=usuario.matricula,
        perfil=usuario.perfil.nome_perfil,
        id_ppc=aluno.id_ppc,
        data_ingresso=aluno.data_ingresso,
        status=aluno.status,
    )


ZERO = Decimal("0")
CEM = Decimal("100")


def calcular_percentual(total_aproveitado: Decimal, total_exigido: Decimal) -> Decimal:
    """total_aproveitado / total_exigido x 100, com 2 casas e sempre entre 0 e 100."""
    percentual = (Decimal(total_aproveitado) * CEM / Decimal(total_exigido)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return min(max(percentual, ZERO), CEM)


def totais_dos_alunos(db: Session, ids_alunos: List[int]) -> dict:
    """Total aproveitado (só as aprovadas) e quantidade de pendentes de cada aluno, em 2 consultas."""
    if not ids_alunos:
        return {}
    aproveitados = dict(
        db.query(models.Solicitacao.id_aluno, func.sum(models.Solicitacao.pontos_aproveitados))
        .filter(models.Solicitacao.id_aluno.in_(ids_alunos), models.Solicitacao.status == "APROVADA")
        .group_by(models.Solicitacao.id_aluno)
        .all()
    )
    pendentes = dict(
        db.query(models.Solicitacao.id_aluno, func.count(models.Solicitacao.id))
        .filter(models.Solicitacao.id_aluno.in_(ids_alunos), models.Solicitacao.status == "PENDENTE")
        .group_by(models.Solicitacao.id_aluno)
        .all()
    )
    return {id_aluno: (aproveitados.get(id_aluno) or ZERO, pendentes.get(id_aluno, 0)) for id_aluno in ids_alunos}


def lista_de_semestres(pontos_por_semestre: dict) -> list:
    """Só os semestres que tiveram pontos, do mais antigo para o mais recente."""
    return [
        {"ano": ano, "semestre": semestre, "aproveitado": pontos}
        for (ano, semestre), pontos in sorted(pontos_por_semestre.items())
        if pontos > 0
    ]


def montar_progresso(db: Session, aluno: models.Aluno) -> dict:
    """Progresso do aluno no PPC dele: todas as categorias e subcategorias, com os limites ao lado."""
    ppc = aluno.ppc
    total_aproveitado, pendentes = totais_dos_alunos(db, [aluno.id])[aluno.id]

    # Pontos aproveitados das aprovadas, somados por subcategoria e semestre
    linhas = (
        db.query(
            models.RegraPontuacao.id_subcategoria,
            models.Solicitacao.ano,
            models.Solicitacao.semestre,
            func.sum(models.Solicitacao.pontos_aproveitados),
        )
        .join(models.RegraPontuacao, models.Solicitacao.id_regra_pontuacao == models.RegraPontuacao.id)
        .filter(models.Solicitacao.id_aluno == aluno.id, models.Solicitacao.status == "APROVADA")
        .group_by(models.RegraPontuacao.id_subcategoria, models.Solicitacao.ano, models.Solicitacao.semestre)
        .all()
    )
    por_subcategoria = defaultdict(dict)
    for id_subcategoria, ano, semestre, pontos in linhas:
        por_subcategoria[id_subcategoria][(ano, semestre)] = pontos or ZERO

    categorias = []
    for categoria in ppc.categorias:
        semestres_categoria = defaultdict(lambda: ZERO)
        subcategorias = []
        for subcategoria in categoria.subcategorias:
            semestres = por_subcategoria.get(subcategoria.id, {})
            for chave, pontos in semestres.items():
                semestres_categoria[chave] += pontos
            subcategorias.append({
                "id": subcategoria.id,
                "codigo": subcategoria.codigo,
                "nome": subcategoria.nome,
                "limite_semestre": subcategoria.limite_semestre,
                "aproveitado_total": sum(semestres.values(), ZERO),
                "semestres": lista_de_semestres(semestres),
            })
        categorias.append({
            "id": categoria.id,
            "nome": categoria.nome,
            "limite_total": categoria.limite_total,
            "limite_semestre": categoria.limite_semestre,
            "aproveitado_total": sum(semestres_categoria.values(), ZERO),
            "semestres": lista_de_semestres(semestres_categoria),
            "subcategorias": subcategorias,
        })

    return {
        "total_exigido": ppc.total_pontos,
        "total_aproveitado": total_aproveitado,
        "percentual": calcular_percentual(total_aproveitado, ppc.total_pontos),
        "pendentes": pendentes,
        "categorias": categorias,
    }


def montar_aluno(aluno: models.Aluno, total_aproveitado: Decimal, pendentes: int) -> dict:
    """Monta o aluno no formato do contrato, com o progresso resumido."""
    usuario = aluno.usuario
    ppc = aluno.ppc
    return {
        "id": aluno.id,
        "id_usuario": aluno.id_usuario,
        "nome": usuario.nome,
        "email": usuario.email,
        "matricula": usuario.matricula,
        "data_ingresso": aluno.data_ingresso,
        "curso": ppc.curso,
        "ppc": ppc,
        "total_exigido": ppc.total_pontos,
        "total_aproveitado": total_aproveitado,
        "percentual": calcular_percentual(total_aproveitado, ppc.total_pontos),
        "pendentes": pendentes,
    }


@router.get("/alunos/me/progresso", response_model=schemas.Progresso)
def meu_progresso(
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_current_aluno),
):
    """O progresso do aluno logado: só contam as solicitações aprovadas."""
    return montar_progresso(db, aluno_do_usuario(usuario))


@router.get("/alunos", response_model=List[schemas.Aluno])
def listar_alunos(
    id_ppc: Optional[int] = Query(None),
    busca: Optional[str] = Query(None, max_length=100),
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_current_validador),
):
    """Alunos com o progresso resumido, em ordem alfabética: só professor e coordenador."""
    # O usuário vem na mesma consulta; o PPC e o curso, uma vez só cada um, porque são poucos
    consulta = db.query(models.Aluno).join(models.Aluno.usuario).options(contains_eager(models.Aluno.usuario))
    if id_ppc is not None:
        consulta = consulta.filter(models.Aluno.id_ppc == id_ppc)
    busca = (busca or "").strip()
    if busca:
        consulta = consulta.filter(or_(
            models.Usuario.nome.icontains(busca, autoescape=True),
            models.Usuario.matricula.icontains(busca, autoescape=True),
        ))
    alunos = consulta.order_by(models.Usuario.nome, models.Aluno.id).all()

    totais = totais_dos_alunos(db, [aluno.id for aluno in alunos])
    return [montar_aluno(aluno, *totais[aluno.id]) for aluno in alunos]


@router.get("/alunos/{id_aluno}", response_model=schemas.AlunoDetalhe)
def detalhar_aluno(
    id_aluno: int,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_current_validador),
):
    """Dados do aluno, o progresso e as solicitações: só professor e coordenador."""
    aluno = db.get(models.Aluno, id_aluno)
    if aluno is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")

    progresso = montar_progresso(db, aluno)
    solicitacoes = (
        db.query(models.Solicitacao)
        .filter(models.Solicitacao.id_aluno == aluno.id)
        .order_by(models.Solicitacao.data_atividade.desc(), models.Solicitacao.id.desc())
        .all()
    )
    return {
        "aluno": montar_aluno(aluno, progresso["total_aproveitado"], progresso["pendentes"]),
        "progresso": progresso,
        "solicitacoes": [montar_solicitacao(solicitacao) for solicitacao in solicitacoes],
    }

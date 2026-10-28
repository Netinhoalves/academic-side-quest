import time
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_coordenador, get_current_user
from app.database import get_db

router = APIRouter(tags=["PPCs"])

@router.get("/cursos/{id_curso}/ppcs", response_model=List[schemas.PPCResumo])
def list_ppcs_by_curso(id_curso: int, db: Session = Depends(get_db)):
    """Lista os PPCs ativos de um curso ativo, do mais recente para o mais antigo (Rota pública)."""
    curso = db.query(models.Curso).filter(models.Curso.id == id_curso, models.Curso.ativo == True).first()
    if not curso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso não encontrado")

    return (
        db.query(models.PPC)
        .filter(models.PPC.id_curso == id_curso, models.PPC.ativo == True)
        .order_by(models.PPC.ano.desc(), models.PPC.id.desc())
        .all()
    )

def validar_curso_e_nome(db: Session, dados: schemas.CadastroPPC, id_ppc: Optional[int] = None):
    """Confere se o curso existe e está ativo e se o nome está livre no curso (na edição, ignora o próprio PPC)."""
    curso = db.query(models.Curso).filter(models.Curso.id == dados.id_curso).first()
    if not curso:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Curso não encontrado")
    if not curso.ativo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Curso inativo")

    repetido = db.query(models.PPC).filter(models.PPC.id_curso == curso.id, models.PPC.nome == dados.nome)
    if id_ppc is not None:
        repetido = repetido.filter(models.PPC.id != id_ppc)
    if repetido.first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe um PPC com esse nome neste curso")

def montar_categorias(dados: schemas.CadastroPPC) -> List[models.Categoria]:
    """Cria as categorias, subcategorias e regras a partir da árvore recebida no JSON."""
    categorias = []
    for cat in dados.categorias:
        categoria = models.Categoria(
            nome=cat.nome,
            descricao=cat.descricao or None,
            limite_total=cat.limite_total,
            limite_semestre=cat.limite_semestre,
        )
        categorias.append(categoria)
        for sub in cat.subcategorias:
            subcategoria = models.Subcategoria(
                codigo=sub.codigo,
                nome=sub.nome,
                descricao=sub.descricao or None,
                documentacao_pedida=sub.documentacao_pedida,
                limite_semestre=sub.limite_semestre,
            )
            categoria.subcategorias.append(subcategoria)
            for regra in sub.regras:
                subcategoria.regras.append(models.RegraPontuacao(
                    titulo_exibicao=regra.titulo_exibicao,
                    tipo=regra.tipo,
                    multiplicador=regra.multiplicador,
                    operacao=regra.operacao,
                    tipo_documento=regra.tipo_documento or sub.documentacao_pedida,
                ))
    return categorias

def salvar_ppc(db: Session, ppc: models.PPC) -> models.PPC:
    """Faz o commit; se o banco recusar, desfaz tudo e responde 409."""
    try:
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        if "uq_ppc_curso_nome" in str(erro.orig):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe um PPC com esse nome neste curso")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Há categorias ou subcategorias repetidas no PPC")

    db.refresh(ppc)
    return ppc

@router.post("/ppcs", response_model=schemas.PPCDetalhe, status_code=status.HTTP_201_CREATED)
def create_ppc(
    dados: schemas.CadastroPPC,
    db: Session = Depends(get_db),
    coordenador: models.Usuario = Depends(get_current_coordenador),
):
    """Cadastra um PPC com categorias, subcategorias e regras em uma única transação (Requer token de Coordenador ou Administrador)."""
    validar_curso_e_nome(db, dados)

    ppc = models.PPC(
        id_curso=dados.id_curso,
        nome=dados.nome,
        ano=dados.ano,
        descricao=dados.descricao or None,
        total_pontos=dados.total_pontos,
        ativo=True,
        id_criador=coordenador.id,
        categorias=montar_categorias(dados),
    )
    db.add(ppc)
    return salvar_ppc(db, ppc)

@router.get("/ppcs", response_model=List[schemas.PPC])
def list_ppcs(
    id_curso: Optional[int] = None,
    db: Session = Depends(get_db),
    coordenador: models.Usuario = Depends(get_current_coordenador),
):
    """Lista os PPCs, ativos e inativos, com filtro opcional por curso (Requer token de Coordenador ou Administrador)."""
    query = db.query(models.PPC)
    if id_curso is not None:
        if not db.query(models.Curso).filter(models.Curso.id == id_curso).first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso não encontrado")
        query = query.filter(models.PPC.id_curso == id_curso)

    return query.order_by(models.PPC.id_curso, models.PPC.ano.desc(), models.PPC.id.desc()).all()

@router.get("/ppcs/{id_ppc}", response_model=schemas.PPCDetalhe)
def get_ppc(
    id_ppc: int,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_current_user),
):
    """Retorna o PPC com categorias, subcategorias e regras (Requer token de qualquer perfil)."""
    ppc = db.query(models.PPC).filter(models.PPC.id == id_ppc).first()
    if not ppc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PPC não encontrado")
    return ppc

def substituir_ppc(db: Session, id_ppc: int, dados: schemas.CadastroPPC) -> models.PPC:
    """Troca os dados e a árvore do PPC em uma transação; o PPC fica travado até o commit."""
    ppc = db.query(models.PPC).filter(models.PPC.id == id_ppc).with_for_update().first()
    if not ppc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PPC não encontrado")
    if ppc.em_uso:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="PPC em uso, não pode ser alterado")

    validar_curso_e_nome(db, dados, id_ppc=ppc.id)

    ids_categorias = select(models.Categoria.id).where(models.Categoria.id_ppc == ppc.id)
    ids_subcategorias = select(models.Subcategoria.id).where(models.Subcategoria.id_categoria.in_(ids_categorias))
    try:
        db.query(models.RegraPontuacao).filter(models.RegraPontuacao.id_subcategoria.in_(ids_subcategorias)).delete(synchronize_session=False)
        db.query(models.Subcategoria).filter(models.Subcategoria.id_categoria.in_(ids_categorias)).delete(synchronize_session=False)
        db.query(models.Categoria).filter(models.Categoria.id_ppc == ppc.id).delete(synchronize_session=False)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="PPC em uso, não pode ser alterado")

    ppc.id_curso = dados.id_curso
    ppc.nome = dados.nome
    ppc.ano = dados.ano
    ppc.descricao = dados.descricao or None
    ppc.total_pontos = dados.total_pontos
    ppc.updated_at = func.now()
    for categoria in montar_categorias(dados):
        categoria.id_ppc = ppc.id
        db.add(categoria)

    return salvar_ppc(db, ppc)

@router.put("/ppcs/{id_ppc}", response_model=schemas.PPCDetalhe)
def update_ppc(
    id_ppc: int,
    dados: schemas.CadastroPPC,
    db: Session = Depends(get_db),
    coordenador: models.Usuario = Depends(get_current_coordenador),
):
    """Substitui os dados e a árvore de um PPC que ainda não tem alunos vinculados (Requer token de Coordenador ou Administrador)."""
    for tentativa in range(1, 4):
        try:
            return substituir_ppc(db, id_ppc, dados)
        except OperationalError as erro:
            # 1213 = deadlock: o MySQL cancelou esta transação por causa de outra edição simultânea; tenta de novo
            db.rollback()
            if erro.orig.args[0] != 1213 or tentativa == 3:
                raise
            time.sleep(0.1 * tentativa)

@router.patch("/ppcs/{id_ppc}/ativo", response_model=schemas.PPC)
def update_ppc_ativo(
    id_ppc: int,
    dados: schemas.AtivacaoPPC,
    db: Session = Depends(get_db),
    coordenador: models.Usuario = Depends(get_current_coordenador),
):
    """Ativa ou desativa um PPC, mesmo que ele tenha alunos vinculados (Requer token de Coordenador ou Administrador)."""
    ppc = db.query(models.PPC).filter(models.PPC.id == id_ppc).first()
    if not ppc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PPC não encontrado")

    ppc.ativo = dados.ativo
    db.commit()
    db.refresh(ppc)
    return ppc

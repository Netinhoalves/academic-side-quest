from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
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

@router.post("/ppcs", response_model=schemas.PPCDetalhe, status_code=status.HTTP_201_CREATED)
def create_ppc(
    dados: schemas.CadastroPPC,
    db: Session = Depends(get_db),
    coordenador: models.Usuario = Depends(get_current_coordenador),
):
    """Cadastra um PPC com categorias, subcategorias e regras em uma única transação (Requer token de Coordenador ou Administrador)."""
    curso = db.query(models.Curso).filter(models.Curso.id == dados.id_curso).first()
    if not curso:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Curso não encontrado")
    if not curso.ativo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Curso inativo")

    if db.query(models.PPC).filter(models.PPC.id_curso == curso.id, models.PPC.nome == dados.nome).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe um PPC com esse nome neste curso")

    ppc = models.PPC(
        id_curso=curso.id,
        nome=dados.nome,
        ano=dados.ano,
        descricao=dados.descricao or None,
        total_pontos=dados.total_pontos,
        ativo=True,
        id_criador=coordenador.id,
    )
    for cat in dados.categorias:
        categoria = models.Categoria(
            nome=cat.nome,
            descricao=cat.descricao or None,
            limite_total=cat.limite_total,
            limite_semestre=cat.limite_semestre,
        )
        ppc.categorias.append(categoria)
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

    try:
        db.add(ppc)
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        if "uq_ppc_curso_nome" in str(erro.orig):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe um PPC com esse nome neste curso")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Há categorias ou subcategorias repetidas no PPC")

    db.refresh(ppc)
    return ppc

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

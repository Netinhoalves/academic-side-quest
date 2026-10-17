from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_coordenador
from app.database import get_db

router = APIRouter(prefix="/cursos", tags=["Cursos"])

def validar_duplicados(db: Session, dados: schemas.CadastroCurso, id_curso: Optional[int] = None):
    """Confere se o nome e a sigla estão livres, incluindo cursos inativos (na edição, ignora o próprio curso)."""
    mesmo_nome = db.query(models.Curso).filter(models.Curso.nome == dados.nome)
    mesma_sigla = db.query(models.Curso).filter(models.Curso.sigla == dados.sigla)
    if id_curso is not None:
        mesmo_nome = mesmo_nome.filter(models.Curso.id != id_curso)
        mesma_sigla = mesma_sigla.filter(models.Curso.id != id_curso)

    if mesmo_nome.first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe um curso com esse nome")
    if mesma_sigla.first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe um curso com essa sigla")

def salvar_curso(db: Session, curso: models.Curso) -> models.Curso:
    """Faz o commit; se o banco recusar a sigla repetida (cadastros simultâneos), desfaz e responde 409."""
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe um curso com essa sigla")

    db.refresh(curso)
    return curso

@router.get("", response_model=List[schemas.Curso])
def list_cursos(db: Session = Depends(get_db)):
    """Lista os cursos ativos em ordem alfabética (Rota pública)."""
    return db.query(models.Curso).filter(models.Curso.ativo == True).order_by(models.Curso.nome).all()

@router.post("", response_model=schemas.Curso, status_code=status.HTTP_201_CREATED)
def create_curso(
    dados: schemas.CadastroCurso,
    db: Session = Depends(get_db),
    coordenador: models.Usuario = Depends(get_current_coordenador),
):
    """Cadastra um curso (Requer token de Coordenador ou Administrador)."""
    validar_duplicados(db, dados)

    curso = models.Curso(nome=dados.nome, sigla=dados.sigla, instituicao=dados.instituicao, ativo=True)
    db.add(curso)
    return salvar_curso(db, curso)

@router.put("/{id_curso}", response_model=schemas.Curso)
def update_curso(
    id_curso: int,
    dados: schemas.CadastroCurso,
    db: Session = Depends(get_db),
    coordenador: models.Usuario = Depends(get_current_coordenador),
):
    """Atualiza nome, sigla e instituição de um curso (Requer token de Coordenador ou Administrador)."""
    curso = db.query(models.Curso).filter(models.Curso.id == id_curso).first()
    if not curso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso não encontrado")

    validar_duplicados(db, dados, id_curso=curso.id)

    curso.nome = dados.nome
    curso.sigla = dados.sigla
    curso.instituicao = dados.instituicao
    return salvar_curso(db, curso)

@router.delete("/{id_curso}", status_code=status.HTTP_204_NO_CONTENT)
def delete_curso(
    id_curso: int,
    db: Session = Depends(get_db),
    coordenador: models.Usuario = Depends(get_current_coordenador),
):
    """Desativa um curso via soft delete (Requer token de Coordenador ou Administrador)."""
    curso = db.query(models.Curso).filter(models.Curso.id == id_curso).first()
    if not curso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso não encontrado")

    curso.ativo = False
    db.commit()
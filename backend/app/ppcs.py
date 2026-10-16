from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
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

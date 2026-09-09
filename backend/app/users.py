from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.auth import get_current_admin

router = APIRouter(prefix="/usuarios", tags=["Gestão de Usuários (Admin)"])

@router.get("", response_model=List[schemas.User])
def list_users(
    id_perfil: Optional[int] = None,
    db: Session = Depends(get_db),
    admin: models.Usuario = Depends(get_current_admin)
):
    """Lista todos os usuários cadastrados (Requer token de Administrador)."""
    query = db.query(models.Usuario)
    if id_perfil:
        query = query.filter(models.Usuario.id_perfil == id_perfil)
    return query.all()

@router.get("/{id}", response_model=schemas.User)
def get_user(
    id: int,
    db: Session = Depends(get_db),
    admin: models.Usuario = Depends(get_current_admin)
):
    """Busca os dados de um usuário pelo ID (Requer token de Administrador)."""
    user = db.query(models.Usuario).filter(models.Usuario.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return user

@router.put("/{id}", response_model=schemas.User)
def update_user(
    id: int,
    data: schemas.UpdateUser,
    db: Session = Depends(get_db),
    admin: models.Usuario = Depends(get_current_admin)
):
    """Atualiza dados cadastrais de um usuário (Requer token de Administrador)."""
    user = db.query(models.Usuario).filter(models.Usuario.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    # Compatibilidade Pydantic v1 / v2
    updates = data.model_dump(exclude_unset=True) if hasattr(data, "model_dump") else data.dict(exclude_unset=True)

    if "email" in updates and updates["email"] != user.email:
        duplicado = db.query(models.Usuario).filter(
            models.Usuario.email == updates["email"],
            models.Usuario.id != id
        ).first()
        if duplicado:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail já cadastrado")

    if updates.get("matricula") and updates["matricula"] != user.matricula:
        duplicado = db.query(models.Usuario).filter(
            models.Usuario.matricula == updates["matricula"],
            models.Usuario.id != id
        ).first()
        if duplicado:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Matrícula já cadastrada")

    for campo, valor in updates.items():
        setattr(user, campo, valor)

    db.commit()
    db.refresh(user)
    return user

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    id: int,
    db: Session = Depends(get_db),
    admin: models.Usuario = Depends(get_current_admin)
):
    """Desativa um usuário no sistema via soft delete (Requer token de Administrador)."""
    if admin.id == id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é permitido desativar o usuário administrador atualmente autenticado"
        )

    user = db.query(models.Usuario).filter(models.Usuario.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    user.ativo = False
    db.commit()
    return None
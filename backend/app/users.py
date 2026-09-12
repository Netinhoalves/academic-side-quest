from typing import Optional

import bcrypt

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_admin
from app.database import get_db
from app.models import Usuario
from app.schemas import CreateUser, UpdateUser, User


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


router = APIRouter(prefix="/usuarios", tags=["Gestão de Usuários (Admin)"])


@router.get("", response_model=list[User])
def list_users(
    id_perfil: Optional[int] = None,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(get_current_admin)
):
    query = db.query(Usuario)
    if id_perfil is not None:
        query = query.filter(Usuario.id_perfil == id_perfil)
    return query.all()


@router.get("/{user_id}", response_model=User)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(get_current_admin)
):
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return user


@router.post("", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(
    data: CreateUser,
    db: Session = Depends(get_db)
):
    if db.query(Usuario).filter(Usuario.email == data.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail já cadastrado")

    if data.matricula and db.query(Usuario).filter(Usuario.matricula == data.matricula).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Matrícula já cadastrada")

    user = Usuario(
        nome=data.nome,
        email=data.email,
        senha_hash=hash_password(data.senha),
        matricula=data.matricula,
        id_perfil=data.id_perfil,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}", response_model=User)
def update_user(
    user_id: int,
    data: UpdateUser,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(get_current_admin)
):
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    updates = data.model_dump(exclude_unset=True) if hasattr(data, "model_dump") else data.dict(exclude_unset=True)

    if "email" in updates and updates["email"] != user.email:
        duplicado = db.query(Usuario).filter(
            Usuario.email == updates["email"],
            Usuario.id != user_id
        ).first()
        if duplicado:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail já cadastrado")

    if updates.get("matricula") and updates["matricula"] != user.matricula:
        duplicado = db.query(Usuario).filter(
            Usuario.matricula == updates["matricula"],
            Usuario.id != user_id
        ).first()
        if duplicado:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Matrícula já cadastrada")

    if "senha" in updates:
        user.senha_hash = hash_password(updates.pop("senha"))

    for campo, valor in updates.items():
        setattr(user, campo, valor)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(get_current_admin)
):
    if admin.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é permitido desativar o usuário administrador atualmente autenticado"
        )

    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    user.ativo = False
    db.commit()
    return None
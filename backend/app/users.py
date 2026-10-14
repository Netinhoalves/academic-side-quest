from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Usuario
from app.schemas import CreateUser, UpdateUser, User
from app.security import hash_password

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("", response_model=list[User])
def list_users(id_perfil: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Usuario)
    if id_perfil:
        query = query.filter(Usuario.id_perfil == id_perfil)
    return query.all()

@router.get("/{user_id}", response_model=User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

@router.post("", response_model=User, status_code=201)
def create_user(data: CreateUser, db: Session = Depends(get_db)):
    if db.query(Usuario).filter(Usuario.email == data.email).first():
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")

    if data.matricula and db.query(Usuario).filter(Usuario.matricula == data.matricula).first():
        raise HTTPException(status_code=409, detail="Matrícula já cadastrada")

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
def update_user(user_id: int, data: UpdateUser, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    updates = data.dict(exclude_unset=True)

    if "email" in updates:
        duplicado = db.query(Usuario).filter(
            Usuario.email == updates["email"], Usuario.id != user_id
        ).first()
        if duplicado:
            raise HTTPException(status_code=409, detail="E-mail já cadastrado")

    if updates.get("matricula"):
        duplicado = db.query(Usuario).filter(
            Usuario.matricula == updates["matricula"], Usuario.id != user_id
        ).first()
        if duplicado:
            raise HTTPException(status_code=409, detail="Matrícula já cadastrada")

    if "senha" in updates:
        user.senha_hash = hash_password(updates.pop("senha"))

    for campo, valor in updates.items():
        setattr(user, campo, valor)

    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    user.ativo = False
    db.commit()
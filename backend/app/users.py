from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_admin, get_current_coordenador
from app.database import get_db
from app.models import Usuario
from app.schemas import CreateUser, UpdateUser, User
from app.security import hash_password

router = APIRouter(prefix="/usuarios", tags=["Gestão de Usuários (Admin)"])

# Quem pode cadastrar quem: ninguém cadastra Administrador nem Aluno por aqui
PERFIS_QUE_PODEM_CRIAR = {
    "Administrador": ("Coordenador", "Professor"),
    "Coordenador": ("Professor",),
}

def buscar_perfil(db: Session, id_perfil: int) -> models.Perfil:
    """Retorna o perfil pelo ID ou responde 400 se ele não existir."""
    perfil = db.query(models.Perfil).filter(models.Perfil.id == id_perfil).first()
    if not perfil:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Perfil não encontrado")
    return perfil

@router.get("", response_model=List[schemas.User])
def list_users(
    id_perfil: Optional[int] = None,
    db: Session = Depends(get_db),
    usuario_atual: models.Usuario = Depends(get_current_coordenador)
):
    """Lista os usuários: o Administrador vê todos e o Coordenador só os professores (Requer token de Coordenador ou Administrador)."""
    query = db.query(models.Usuario)
    if usuario_atual.perfil.nome_perfil == "Coordenador":
        query = query.filter(models.Usuario.perfil.has(models.Perfil.nome_perfil.in_(PERFIS_QUE_PODEM_CRIAR["Coordenador"])))
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

@router.post("", response_model=User, status_code=201)
def create_user(
    data: CreateUser,
    db: Session = Depends(get_db),
    criador: models.Usuario = Depends(get_current_coordenador)
):
    """Cadastra um servidor: o Administrador cria Coordenador ou Professor e o Coordenador cria apenas Professor (Requer token de Coordenador ou Administrador)."""
    perfil = buscar_perfil(db, data.id_perfil)
    permitidos = PERFIS_QUE_PODEM_CRIAR[criador.perfil.nome_perfil]
    if perfil.nome_perfil not in permitidos:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acesso negado: {criador.perfil.nome_perfil} só pode cadastrar usuários com perfil {' ou '.join(permitidos)}"
        )

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

    try:
        db.add(user)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail ou matrícula já cadastrados")

    db.refresh(user)
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

    updates = data.model_dump(exclude_unset=True) if hasattr(data, "model_dump") else data.dict(exclude_unset=True)

    if user.id == admin.id and (updates.get("ativo") is False or updates.get("id_perfil", user.id_perfil) != user.id_perfil):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é permitido desativar nem trocar o perfil do próprio usuário"
        )

    if "id_perfil" in updates and updates["id_perfil"] != user.id_perfil:
        novo_perfil = buscar_perfil(db, updates["id_perfil"])
        if novo_perfil.nome_perfil not in PERFIS_QUE_PODEM_CRIAR["Administrador"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado: o perfil só pode ser trocado para Coordenador ou Professor"
            )

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

    if "senha" in updates:
        user.senha_hash = hash_password(updates.pop("senha"))

    for campo, valor in updates.items():
        setattr(user, campo, valor)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail ou matrícula já cadastrados")

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
import os
import datetime
import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

SECRET_KEY = os.getenv("SECRET_KEY", "chave_super_secreta_provisoria")
ALGORITHM = "HS256"

security = HTTPBearer()

router = APIRouter()

@router.post("/login")
def login(req: schemas.LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.email == req.email).first()

    if not usuario:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha inválidos")

    hash_salvo = usuario.senha_hash or ""
    try:
        senha_valida = bcrypt.checkpw(req.senha.encode('utf-8'), hash_salvo.encode('utf-8'))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha inválidos")

    if not senha_valida:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha inválidos")

    nome_perfil = usuario.perfil.nome_perfil if usuario.perfil else "Sem Perfil"

    payload = {
        "sub": usuario.email,
        "id": usuario.id,
        "perfil": nome_perfil,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "sucesso": True,
        "token": token,
        "usuario": {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "perfil": nome_perfil,
        },
    }

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> models.Usuario:
    """Extrai e valida o token JWT, retornando o usuário ativo correspondente."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de autenticação inválido: identificador ausente",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acesso inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    usuario = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inativo no sistema",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return usuario

def get_current_admin(
    usuario_atual: models.Usuario = Depends(get_current_user)
) -> models.Usuario:
    """Garante que o usuário autenticado possua o perfil 'Administrador'."""
    if not usuario_atual.perfil or usuario_atual.perfil.nome_perfil != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: recurso restrito a usuários com perfil Administrador"
        )
    return usuario_atual
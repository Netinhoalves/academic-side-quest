import datetime
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY, verify_password

security = HTTPBearer()

router = APIRouter()

@router.post("/login")
def login(req: schemas.LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.email == req.email).first()

    if not usuario:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha inválidos")

    if not verify_password(req.senha, usuario.senha_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha inválidos")

    if not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Usuário inativo. Entre em contato com o administrador."
        )

    nome_perfil = usuario.perfil.nome_perfil if usuario.perfil else "Sem Perfil"

    payload = {
        "sub": usuario.email,
        "id": usuario.id,
        "perfil": nome_perfil,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"sucesso": True, "token": token}

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

def get_current_coordenador(
    usuario_atual: models.Usuario = Depends(get_current_user)
) -> models.Usuario:
    """Garante que o usuário autenticado possua o perfil 'Coordenador' ou 'Administrador'."""
    if not usuario_atual.perfil or usuario_atual.perfil.nome_perfil not in ("Coordenador", "Administrador"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: recurso restrito a usuários com perfil Coordenador ou Administrador"
        )
    return usuario_atual


def get_current_validador(
    usuario_atual: models.Usuario = Depends(get_current_user)
) -> models.Usuario:
    """Garante que o usuário autenticado possua o perfil 'Professor' ou 'Coordenador' (validação de horas)."""
    if not usuario_atual.perfil or usuario_atual.perfil.nome_perfil not in ("Professor", "Coordenador"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: recurso restrito a usuários com perfil Professor ou Coordenador"
        )
    return usuario_atual


def get_current_aluno(
    usuario_atual: models.Usuario = Depends(get_current_user)
) -> models.Usuario:
    """Garante que o usuário autenticado possua o perfil 'Aluno'."""
    if not usuario_atual.perfil or usuario_atual.perfil.nome_perfil != "Aluno":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: recurso restrito a usuários com perfil Aluno"
        )
    return usuario_atual


def get_student_data(usuario: models.Usuario):
    return None, None


@router.get("/me", response_model=schemas.CurrentUser)
def get_me(usuario_atual: models.Usuario = Depends(get_current_user)):
    nome_perfil = usuario_atual.perfil.nome_perfil if usuario_atual.perfil else None

    curso, ppc = None, None
    if nome_perfil == "Aluno":
        curso, ppc = get_student_data(usuario_atual)

    return schemas.CurrentUser(
        id=usuario_atual.id,
        nome=usuario_atual.nome,
        email=usuario_atual.email,
        matricula=usuario_atual.matricula,
        perfil=nome_perfil,
        curso=curso,
        ppc=ppc,
    )
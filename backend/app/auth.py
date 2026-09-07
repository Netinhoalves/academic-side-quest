import bcrypt
import jwt
import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

SECRET_KEY = "chave_super_secreta_provisoria" 

router = APIRouter()

@router.post("/login")
def login(req: schemas.LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.email == req.email).first()
    
    if not usuario:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha inválidos")
    
    if not bcrypt.checkpw(req.senha.encode('utf-8'), usuario.senha_hash.encode('utf-8')):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha inválidos")
    
    nome_perfil = usuario.perfil.nome_perfil if usuario.perfil else "Sem Perfil"

    payload = {
        "sub": usuario.email,
        "perfil": nome_perfil,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    
    return {"sucesso": True, "token": token}
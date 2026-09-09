from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class Profile(BaseModel):
    id: int
    nome_perfil: str

    model_config = ConfigDict(from_attributes=True)

class BaseUser(BaseModel):
    nome: str
    email: str
    matricula: Optional[str] = None
    id_perfil: int

class CreateUser(BaseUser):
    senha: str

class UpdateUser(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    senha: Optional[str] = None
    matricula: Optional[str] = None
    id_perfil: Optional[int] = None
    ativo: Optional[bool] = None

class User(BaseUser):
    id: int
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
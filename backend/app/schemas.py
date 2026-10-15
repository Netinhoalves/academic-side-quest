from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional
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


class LoginRequest(BaseModel):
    email: str
    senha: str


class Curso(BaseModel):
    id: int
    nome: str
    sigla: str
    instituicao: str
    ativo: bool

    model_config = ConfigDict(from_attributes=True)

class PPC(BaseModel):
    id: int
    id_curso: int
    nome: str
    ano: int
    descricao: Optional[str] = None
    total_pontos: Decimal
    ativo: bool
    id_criador: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Categoria(BaseModel):
    id: int
    id_ppc: int
    nome: str
    descricao: Optional[str] = None
    limite_total: Decimal
    limite_semestre: Decimal

    model_config = ConfigDict(from_attributes=True)

class Subcategoria(BaseModel):
    id: int
    id_categoria: int
    codigo: str
    nome: str
    descricao: Optional[str] = None
    documentacao_pedida: str
    limite_semestre: Decimal

    model_config = ConfigDict(from_attributes=True)

class RegraPontuacao(BaseModel):
    id: int
    id_subcategoria: int
    titulo_exibicao: str
    tipo: str
    multiplicador: Decimal
    operacao: Literal["SOMA", "MULTIPLICACAO"]
    tipo_documento: str

    model_config = ConfigDict(from_attributes=True)

class Aluno(BaseModel):
    id: int
    id_usuario: int
    id_ppc: int
    data_ingresso: date
    status: str

    model_config = ConfigDict(from_attributes=True)

class Solicitacao(BaseModel):
    id: int
    id_aluno: int
    id_regra_pontuacao: int
    descricao_atividade: str
    data_atividade: date
    ano: int
    semestre: int
    quantidade: Optional[Decimal] = None
    arquivo: str
    pontos_calculados: Decimal
    pontos_aproveitados: Optional[Decimal] = None
    status: Literal["PENDENTE", "APROVADA", "REJEITADA"]
    id_avaliador: Optional[int] = None
    observacao: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
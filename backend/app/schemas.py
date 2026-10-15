import re
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Literal, Optional
from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator
from pydantic_core import PydanticCustomError

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

class PPCResumo(BaseModel):
    id: int
    nome: str
    ano: int

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

class CadastroAluno(BaseModel):
    nome: Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=150)]
    email: Annotated[str, StringConstraints(strip_whitespace=True)]
    senha: str
    matricula: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=30)]
    id_ppc: int
    data_ingresso: Optional[date] = None

    @field_validator("email")
    @classmethod
    def validar_email(cls, valor: str) -> str:
        valor = valor.lower()
        if len(valor) > 150:
            raise PydanticCustomError("valor_invalido", "O e-mail deve ter no máximo 150 caracteres")
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", valor):
            raise PydanticCustomError("valor_invalido", "E-mail inválido")
        return valor

    @field_validator("senha")
    @classmethod
    def validar_senha(cls, valor: str) -> str:
        if len(valor) < 6:
            raise PydanticCustomError("valor_invalido", "A senha deve ter pelo menos 6 caracteres")
        if len(valor.encode("utf-8")) > 72:
            raise PydanticCustomError("valor_invalido", "A senha deve ter no máximo 72 bytes")
        return valor

    @field_validator("data_ingresso")
    @classmethod
    def validar_data_ingresso(cls, valor: Optional[date]) -> Optional[date]:
        if valor is not None and valor > date.today():
            raise PydanticCustomError("valor_invalido", "A data de ingresso não pode ser futura")
        return valor

class AlunoCadastrado(BaseModel):
    id_usuario: int
    id_aluno: int
    nome: str
    email: str
    matricula: str
    perfil: str
    id_ppc: int
    data_ingresso: date
    status: str

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
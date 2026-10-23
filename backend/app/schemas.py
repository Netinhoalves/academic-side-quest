import re
import unicodedata
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, List, Literal, Optional
from pydantic import AfterValidator, BaseModel, ConfigDict, Field, PlainSerializer, StringConstraints, ValidationInfo, field_validator, model_validator
from pydantic_core import PydanticCustomError

# Valores de pontos saem como número no JSON (o padrão do Pydantic para Decimal é texto, "275.00")
Pontos = Annotated[Decimal, PlainSerializer(float, return_type=float, when_used="json")]

ValorPositivo = Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]
Texto150 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=150)]
Texto255 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
TextoOpcional = Annotated[str, StringConstraints(strip_whitespace=True, max_length=5000)]

def chave_comparacao(texto: str) -> str:
    """Normaliza o texto como a collation do banco (utf8mb4_0900_ai_ci): ignora maiúsculas e acentos."""
    sem_acento = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in sem_acento if not unicodedata.combining(c)).casefold()

def validar_nome(valor: str) -> str:
    """Tira os espaços das pontas e confere o tamanho do nome (de 3 a 150 caracteres)."""
    valor = valor.strip()
    if len(valor) < 3:
        raise PydanticCustomError("valor_invalido", "O nome deve ter pelo menos 3 caracteres")
    if len(valor) > 150:
        raise PydanticCustomError("valor_invalido", "O nome deve ter no máximo 150 caracteres")
    return valor

def validar_email(valor: str) -> str:
    """Padroniza o e-mail em minúsculas e confere o formato e o tamanho (até 150 caracteres)."""
    valor = valor.strip().lower()
    if len(valor) > 150:
        raise PydanticCustomError("valor_invalido", "O e-mail deve ter no máximo 150 caracteres")
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", valor):
        raise PydanticCustomError("valor_invalido", "E-mail inválido")
    return valor

def validar_senha(valor: str) -> str:
    """Confere o tamanho da senha: pelo menos 6 caracteres e no máximo 72 bytes (limite do bcrypt)."""
    if len(valor) < 6:
        raise PydanticCustomError("valor_invalido", "A senha deve ter pelo menos 6 caracteres")
    if len(valor.encode("utf-8")) > 72:
        raise PydanticCustomError("valor_invalido", "A senha deve ter no máximo 72 bytes")
    return valor

def validar_matricula_servidor(valor: Optional[str]) -> Optional[str]:
    """A matrícula de servidor é opcional: em branco vira None, para não repetir "" na coluna UNIQUE."""
    if valor is None or not valor.strip():
        return None
    valor = valor.strip()
    if len(valor) > 30:
        raise PydanticCustomError("valor_invalido", "A matrícula deve ter no máximo 30 caracteres")
    return valor

Nome = Annotated[str, AfterValidator(validar_nome)]
Email = Annotated[str, AfterValidator(validar_email)]
Senha = Annotated[str, AfterValidator(validar_senha)]
MatriculaServidor = Annotated[Optional[str], AfterValidator(validar_matricula_servidor)]

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
    nome: Nome
    email: Email
    matricula: MatriculaServidor = None
    senha: Senha

class UpdateUser(BaseModel):
    nome: Optional[Nome] = None
    email: Optional[Email] = None
    senha: Optional[Senha] = None
    matricula: MatriculaServidor = None
    id_perfil: Optional[int] = None
    ativo: Optional[bool] = None

    @field_validator("nome", "email", "senha", "id_perfil", "ativo", mode="before")
    @classmethod
    def recusar_nulo(cls, valor, info: ValidationInfo):
        """Esses campos podem ficar de fora do JSON, mas não podem vir como null (as colunas são NOT NULL)."""
        if valor is None:
            raise PydanticCustomError("valor_invalido", f"O campo {info.field_name} não pode ser nulo")
        return valor

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

class CadastroCurso(BaseModel):
    nome: Texto150
    sigla: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=30)]
    instituicao: Texto150

class PPC(BaseModel):
    id: int
    id_curso: int
    nome: str
    ano: int
    descricao: Optional[str] = None
    total_pontos: Pontos
    ativo: bool
    em_uso: bool
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
    limite_total: Pontos
    limite_semestre: Pontos

    model_config = ConfigDict(from_attributes=True)

class Subcategoria(BaseModel):
    id: int
    id_categoria: int
    codigo: str
    nome: str
    descricao: Optional[str] = None
    documentacao_pedida: str
    limite_semestre: Pontos

    model_config = ConfigDict(from_attributes=True)

class RegraPontuacao(BaseModel):
    id: int
    id_subcategoria: int
    titulo_exibicao: str
    tipo: str
    multiplicador: Pontos
    operacao: Literal["SOMA", "MULTIPLICACAO"]
    tipo_documento: str

    model_config = ConfigDict(from_attributes=True)

class SubcategoriaDetalhe(Subcategoria):
    regras: List[RegraPontuacao]

class CategoriaDetalhe(Categoria):
    subcategorias: List[SubcategoriaDetalhe]

class PPCDetalhe(PPC):
    curso: Curso
    categorias: List[CategoriaDetalhe]

class CadastroRegra(BaseModel):
    titulo_exibicao: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]
    tipo: Texto255
    multiplicador: ValorPositivo
    operacao: Literal["SOMA", "MULTIPLICACAO"]
    tipo_documento: Optional[Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)]] = None

class CadastroSubcategoria(BaseModel):
    codigo: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20)]
    nome: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]
    descricao: Optional[TextoOpcional] = None
    documentacao_pedida: Texto255
    limite_semestre: ValorPositivo
    regras: List[CadastroRegra] = Field(min_length=1)

class CadastroCategoria(BaseModel):
    nome: Texto150
    descricao: Optional[TextoOpcional] = None
    limite_total: ValorPositivo
    limite_semestre: ValorPositivo
    subcategorias: List[CadastroSubcategoria] = Field(min_length=1)

    @model_validator(mode="after")
    def validar_limites_e_nomes(self):
        if self.limite_semestre > self.limite_total:
            raise PydanticCustomError(
                "valor_invalido",
                "Categoria '{categoria}': o limite por semestre não pode ser maior que o limite total",
                {"categoria": self.nome},
            )
        nomes = set()
        for sub in self.subcategorias:
            if sub.limite_semestre > self.limite_semestre:
                raise PydanticCustomError(
                    "valor_invalido",
                    "Subcategoria {codigo}: o limite por semestre não pode ser maior que o da categoria",
                    {"codigo": sub.codigo},
                )
            chave = chave_comparacao(sub.nome)
            if chave in nomes:
                raise PydanticCustomError(
                    "valor_invalido",
                    "Subcategoria repetida na categoria '{categoria}': {subcategoria}",
                    {"categoria": self.nome, "subcategoria": sub.nome},
                )
            nomes.add(chave)
        return self

class CadastroPPC(BaseModel):
    id_curso: int
    nome: Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=150)]
    ano: Annotated[int, Field(ge=1900, le=2100)]
    descricao: Optional[TextoOpcional] = None
    total_pontos: ValorPositivo
    categorias: List[CadastroCategoria] = Field(min_length=1)

    @model_validator(mode="after")
    def validar_arvore(self):
        nomes, codigos = set(), set()
        for cat in self.categorias:
            chave = chave_comparacao(cat.nome)
            if chave in nomes:
                raise PydanticCustomError("valor_invalido", "Categoria repetida: {categoria}", {"categoria": cat.nome})
            nomes.add(chave)
            for sub in cat.subcategorias:
                chave = chave_comparacao(sub.codigo)
                if chave in codigos:
                    raise PydanticCustomError("valor_invalido", "Código de subcategoria repetido: {codigo}", {"codigo": sub.codigo})
                codigos.add(chave)
        soma = sum(cat.limite_total for cat in self.categorias)
        if soma < self.total_pontos:
            raise PydanticCustomError(
                "valor_invalido",
                "A soma dos limites totais das categorias ({soma}) é menor que o total de pontos do PPC ({total})",
                {"soma": f"{float(soma):g}", "total": f"{float(self.total_pontos):g}"},
            )
        return self

class AtivacaoPPC(BaseModel):
    ativo: bool

class Aluno(BaseModel):
    id: int
    id_usuario: int
    id_ppc: int
    data_ingresso: date
    status: str

    model_config = ConfigDict(from_attributes=True)

class CadastroAluno(BaseModel):
    nome: Nome
    email: Email
    senha: Senha
    matricula: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=30)]
    id_ppc: int
    data_ingresso: Optional[date] = None

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
    quantidade: Optional[Pontos] = None
    arquivo: str
    pontos_calculados: Pontos
    pontos_aproveitados: Optional[Pontos] = None
    status: Literal["PENDENTE", "APROVADA", "REJEITADA"]
    id_avaliador: Optional[int] = None
    observacao: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CurrentUser(BaseModel):
    id: int
    nome: str
    email: str
    matricula: Optional[str] = None
    perfil: Optional[str] = None
    curso: Optional[Curso] = None
    ppc: Optional[PPCResumo] = None
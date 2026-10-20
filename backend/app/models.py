from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    exists,
    func,
)
from sqlalchemy.orm import column_property, relationship
from app.database import Base

class Perfil(Base):
    __tablename__ = "Perfil"

    id = Column(Integer, primary_key=True)
    nome_perfil = Column(String(50), nullable=False, unique=True)

    usuarios = relationship("Usuario", back_populates="perfil")

class Usuario(Base):
    __tablename__ = "Usuario"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    senha_hash = Column(String(255), nullable=False)
    matricula = Column(String(30), unique=True)
    id_perfil = Column(Integer, ForeignKey("Perfil.id"), nullable=False)
    ativo = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    perfil = relationship("Perfil", back_populates="usuarios")
    ppcs_criados = relationship("PPC", back_populates="criador")
    aluno = relationship("Aluno", back_populates="usuario", uselist=False)
    solicitacoes_avaliadas = relationship("Solicitacao", back_populates="avaliador")

class Curso(Base):
    __tablename__ = "Curso"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(150), nullable=False)
    sigla = Column(String(30), nullable=False, unique=True)
    instituicao = Column(String(150), nullable=False)
    ativo = Column(Boolean, nullable=False, default=True)

    ppcs = relationship("PPC", back_populates="curso")

class PPC(Base):
    __tablename__ = "PPC"
    __table_args__ = (
        UniqueConstraint("id_curso", "nome", name="uq_ppc_curso_nome"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_curso = Column(Integer, ForeignKey("Curso.id"), nullable=False)
    nome = Column(String(150), nullable=False)
    ano = Column(SmallInteger, nullable=False)
    descricao = Column(Text)
    total_pontos = Column(Numeric(10, 2), nullable=False)
    ativo = Column(Boolean, nullable=False, default=True)
    id_criador = Column(Integer, ForeignKey("Usuario.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    curso = relationship("Curso", back_populates="ppcs")
    criador = relationship("Usuario", back_populates="ppcs_criados")
    categorias = relationship("Categoria", back_populates="ppc", order_by="Categoria.id")
    alunos = relationship("Aluno", back_populates="ppc")

class Categoria(Base):
    __tablename__ = "Categoria"
    __table_args__ = (
        UniqueConstraint("id_ppc", "nome", name="uq_categoria_ppc_nome"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_ppc = Column(Integer, ForeignKey("PPC.id"), nullable=False)
    nome = Column(String(150), nullable=False)
    descricao = Column(Text)
    limite_total = Column(Numeric(10, 2), nullable=False)
    limite_semestre = Column(Numeric(10, 2), nullable=False)

    ppc = relationship("PPC", back_populates="categorias")
    subcategorias = relationship("Subcategoria", back_populates="categoria", order_by="Subcategoria.id")

class Subcategoria(Base):
    __tablename__ = "Subcategoria"
    __table_args__ = (
        UniqueConstraint("id_categoria", "nome", name="uq_subcategoria_categoria_nome"),
        UniqueConstraint("id_categoria", "codigo", name="uq_subcategoria_categoria_codigo"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_categoria = Column(Integer, ForeignKey("Categoria.id"), nullable=False)
    codigo = Column(String(20), nullable=False)
    nome = Column(String(500), nullable=False)
    descricao = Column(Text)
    documentacao_pedida = Column(String(255), nullable=False)
    limite_semestre = Column(Numeric(10, 2), nullable=False)

    categoria = relationship("Categoria", back_populates="subcategorias")
    regras = relationship("RegraPontuacao", back_populates="subcategoria", order_by="RegraPontuacao.id")

class RegraPontuacao(Base):
    __tablename__ = "RegraPontuacao"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_subcategoria = Column(Integer, ForeignKey("Subcategoria.id"), nullable=False)
    titulo_exibicao = Column(String(1000), nullable=False)
    tipo = Column(String(255), nullable=False)
    multiplicador = Column(Numeric(10, 2), nullable=False)
    operacao = Column(Enum("SOMA", "MULTIPLICACAO"), nullable=False)
    tipo_documento = Column(String(255), nullable=False)

    subcategoria = relationship("Subcategoria", back_populates="regras")
    solicitacoes = relationship("Solicitacao", back_populates="regra")

class Aluno(Base):
    __tablename__ = "Aluno"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("Usuario.id"), nullable=False, unique=True)
    id_ppc = Column(Integer, ForeignKey("PPC.id"), nullable=False)
    data_ingresso = Column(Date, nullable=False)
    status = Column(String(30), nullable=False, default="ATIVO")

    usuario = relationship("Usuario", back_populates="aluno")
    ppc = relationship("PPC", back_populates="alunos")
    solicitacoes = relationship("Solicitacao", back_populates="aluno")

# Coluna calculada: True quando existe aluno vinculado ao PPC (a edição do PPC fica bloqueada)
PPC.em_uso = column_property(exists().where(Aluno.id_ppc == PPC.id))

class Solicitacao(Base):
    __tablename__ = "Solicitacao"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_aluno = Column(Integer, ForeignKey("Aluno.id"), nullable=False)
    id_regra_pontuacao = Column(Integer, ForeignKey("RegraPontuacao.id"), nullable=False)
    descricao_atividade = Column(Text, nullable=False)
    data_atividade = Column(Date, nullable=False)
    ano = Column(SmallInteger, nullable=False)
    semestre = Column(SmallInteger, nullable=False)
    quantidade = Column(Numeric(10, 2))
    arquivo = Column(String(500), nullable=False)
    pontos_calculados = Column(Numeric(10, 2), nullable=False)
    pontos_aproveitados = Column(Numeric(10, 2))
    status = Column(Enum("PENDENTE", "APROVADA", "REJEITADA"), nullable=False, default="PENDENTE")
    id_avaliador = Column(Integer, ForeignKey("Usuario.id"))
    observacao = Column(Text)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    aluno = relationship("Aluno", back_populates="solicitacoes")
    regra = relationship("RegraPontuacao", back_populates="solicitacoes")
    avaliador = relationship("Usuario", back_populates="solicitacoes_avaliadas")

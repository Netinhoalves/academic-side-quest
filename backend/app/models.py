from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship
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
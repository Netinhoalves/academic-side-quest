from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import hash_password

router = APIRouter(tags=["Alunos"])

@router.post("/auth/cadastro-aluno", response_model=schemas.AlunoCadastrado, status_code=status.HTTP_201_CREATED)
def create_aluno(dados: schemas.CadastroAluno, db: Session = Depends(get_db)):
    """Cadastra um aluno com perfil Aluno vinculado a um PPC ativo (Rota pública)."""
    if db.query(models.Usuario).filter(models.Usuario.email == dados.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail já cadastrado")

    if db.query(models.Usuario).filter(models.Usuario.matricula == dados.matricula).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Matrícula já cadastrada")

    ppc = db.query(models.PPC).filter(models.PPC.id == dados.id_ppc).first()
    if not ppc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="PPC não encontrado")
    if not ppc.ativo or not ppc.curso.ativo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="PPC inativo")

    perfil_aluno = db.query(models.Perfil).filter(models.Perfil.nome_perfil == "Aluno").first()
    if not perfil_aluno:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Perfil Aluno não configurado")

    usuario = models.Usuario(
        nome=dados.nome,
        email=dados.email,
        senha_hash=hash_password(dados.senha),
        matricula=dados.matricula,
        id_perfil=perfil_aluno.id,
        ativo=True,
    )

    try:
        db.add(usuario)
        db.flush()
        aluno = models.Aluno(
            id_usuario=usuario.id,
            id_ppc=ppc.id,
            data_ingresso=dados.data_ingresso or date.today(),
            status="ATIVO",
        )
        db.add(aluno)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail ou matrícula já cadastrados")

    db.refresh(usuario)
    db.refresh(aluno)
    return schemas.AlunoCadastrado(
        id_usuario=usuario.id,
        id_aluno=aluno.id,
        nome=usuario.nome,
        email=usuario.email,
        matricula=usuario.matricula,
        perfil=usuario.perfil.nome_perfil,
        id_ppc=aluno.id_ppc,
        data_ingresso=aluno.data_ingresso,
        status=aluno.status,
    )

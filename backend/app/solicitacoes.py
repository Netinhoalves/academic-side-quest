import calendar
import os
import uuid
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_aluno, get_current_user
from app.database import get_db

router = APIRouter(tags=["Solicitações"])

TAMANHO_MAXIMO = 5 * 1024 * 1024
QUANTIDADE_MAXIMA = Decimal("10000")
CENTAVOS = Decimal("0.01")
# O tipo do comprovante é conferido pelos primeiros bytes do arquivo, não pelo nome enviado
ASSINATURAS = {
    b"%PDF-": (".pdf", "application/pdf"),
    b"\x89PNG\r\n\x1a\n": (".png", "image/png"),
    b"\xff\xd8\xff": (".jpg", "image/jpeg"),
}
TIPOS_POR_EXTENSAO = {extensao: tipo for extensao, tipo in ASSINATURAS.values()}


def pasta_comprovantes() -> Path:
    """Pasta dos comprovantes: UPLOAD_DIR no Docker; backend/uploads quando a API roda direto no computador."""
    pasta = Path(os.getenv("UPLOAD_DIR") or Path(__file__).resolve().parents[1] / "uploads")
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def seis_meses_antes(dia: date) -> date:
    ano, mes = (dia.year, dia.month - 6) if dia.month > 6 else (dia.year - 1, dia.month + 6)
    return date(ano, mes, min(dia.day, calendar.monthrange(ano, mes)[1]))


def erro_validacao(mensagem: str):
    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=mensagem)


def montar_solicitacao(solicitacao: models.Solicitacao) -> dict:
    """Monta a solicitação no formato do contrato, com os nomes da regra, da subcategoria e da categoria."""
    regra = solicitacao.regra
    subcategoria = regra.subcategoria
    usuario_aluno = solicitacao.aluno.usuario
    avaliador = solicitacao.avaliador
    return {
        "id": solicitacao.id,
        "aluno": {"id": solicitacao.id_aluno, "nome": usuario_aluno.nome, "matricula": usuario_aluno.matricula},
        "descricao_atividade": solicitacao.descricao_atividade,
        "data_atividade": solicitacao.data_atividade,
        "ano": solicitacao.ano,
        "semestre": solicitacao.semestre,
        "quantidade": solicitacao.quantidade,
        "pontos_calculados": solicitacao.pontos_calculados,
        "pontos_aproveitados": solicitacao.pontos_aproveitados,
        "status": solicitacao.status,
        "observacao": solicitacao.observacao,
        "regra": regra,
        "subcategoria": subcategoria,
        "categoria": subcategoria.categoria,
        "avaliador": {"id": avaliador.id, "nome": avaliador.nome} if avaliador else None,
        "created_at": solicitacao.created_at,
        "updated_at": solicitacao.updated_at,
    }


def aluno_do_usuario(usuario: models.Usuario) -> models.Aluno:
    if usuario.aluno is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Aluno sem PPC vinculado")
    return usuario.aluno


@router.post("/solicitacoes", response_model=schemas.Solicitacao, status_code=status.HTTP_201_CREATED)
def enviar_solicitacao(
    id_regra_pontuacao: int = Form(...),
    descricao_atividade: str = Form(...),
    data_atividade: date = Form(...),
    quantidade: Optional[Decimal] = Form(None),
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_current_aluno),
):
    """Envio de uma atividade com o comprovante (PDF, JPG ou PNG, até 5 MB)."""
    aluno = aluno_do_usuario(usuario)

    regra = db.get(models.RegraPontuacao, id_regra_pontuacao)
    if regra is None or regra.subcategoria.categoria.id_ppc != aluno.id_ppc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A regra não pertence ao PPC do aluno")

    descricao_atividade = descricao_atividade.strip()
    if not 3 <= len(descricao_atividade) <= 500:
        erro_validacao("A descrição da atividade deve ter de 3 a 500 caracteres")

    hoje = date.today()
    if data_atividade > hoje:
        erro_validacao("A data da atividade não pode ser futura")
    if data_atividade < seis_meses_antes(hoje):
        erro_validacao("A atividade deve ter sido realizada nos últimos 6 meses")

    if regra.operacao == "MULTIPLICACAO":
        if quantidade is None:
            erro_validacao("Informe a quantidade")
        if quantidade <= 0 or quantidade > QUANTIDADE_MAXIMA or quantidade != quantidade.quantize(CENTAVOS):
            erro_validacao("A quantidade deve ser maior que zero, até 10000, com no máximo 2 casas decimais")
        pontos_calculados = (regra.multiplicador * quantidade).quantize(CENTAVOS, rounding=ROUND_HALF_UP)
    else:
        # Nas regras SOMA a quantidade não é usada: vale o valor fixo da regra
        quantidade = None
        pontos_calculados = regra.multiplicador

    conteudo = arquivo.file.read(TAMANHO_MAXIMO + 1)
    if len(conteudo) > TAMANHO_MAXIMO:
        raise HTTPException(status_code=status.HTTP_413_CONTENT_TOO_LARGE, detail="O arquivo deve ter no máximo 5 MB")
    extensao = next((ext for assinatura, (ext, _) in ASSINATURAS.items() if conteudo.startswith(assinatura)), None)
    if extensao is None:
        erro_validacao("O arquivo deve ser PDF, JPG ou PNG")

    # O nome no disco é gerado aqui: o nome enviado pelo usuário nunca entra no caminho
    caminho = pasta_comprovantes() / f"{uuid.uuid4().hex}{extensao}"
    caminho.write_bytes(conteudo)

    solicitacao = models.Solicitacao(
        id_aluno=aluno.id,
        id_regra_pontuacao=regra.id,
        descricao_atividade=descricao_atividade,
        data_atividade=data_atividade,
        ano=data_atividade.year,
        semestre=1 if data_atividade.month <= 6 else 2,
        quantidade=quantidade,
        arquivo=caminho.name,
        pontos_calculados=pontos_calculados,
        status="PENDENTE",
    )
    db.add(solicitacao)
    try:
        db.commit()
    except Exception:
        db.rollback()
        caminho.unlink(missing_ok=True)
        raise
    db.refresh(solicitacao)
    return montar_solicitacao(solicitacao)


@router.get("/alunos/me/solicitacoes", response_model=List[schemas.Solicitacao])
def listar_minhas_solicitacoes(
    status_solicitacao: Optional[Literal["PENDENTE", "APROVADA", "REJEITADA"]] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_current_aluno),
):
    """As solicitações do aluno logado, da atividade mais recente para a mais antiga."""
    aluno = aluno_do_usuario(usuario)
    consulta = db.query(models.Solicitacao).filter(models.Solicitacao.id_aluno == aluno.id)
    if status_solicitacao:
        consulta = consulta.filter(models.Solicitacao.status == status_solicitacao)
    solicitacoes = consulta.order_by(models.Solicitacao.data_atividade.desc(), models.Solicitacao.id.desc()).all()
    return [montar_solicitacao(solicitacao) for solicitacao in solicitacoes]


@router.get("/solicitacoes/{id_solicitacao}/arquivo")
def baixar_comprovante(
    id_solicitacao: int,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_current_user),
):
    """O comprovante da solicitação: só o aluno dono, professor e coordenador."""
    solicitacao = db.get(models.Solicitacao, id_solicitacao)
    if solicitacao is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitação não encontrada")

    perfil = usuario.perfil.nome_perfil if usuario.perfil else None
    if perfil == "Aluno":
        if solicitacao.aluno.id_usuario != usuario.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado: o comprovante é de outro aluno")
    elif perfil not in ("Professor", "Coordenador"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: recurso restrito ao aluno dono, ao professor e ao coordenador",
        )

    caminho = pasta_comprovantes() / Path(solicitacao.arquivo).name
    if not caminho.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comprovante não encontrado")
    return FileResponse(
        caminho,
        media_type=TIPOS_POR_EXTENSAO.get(caminho.suffix, "application/octet-stream"),
        filename=f"comprovante-{solicitacao.id}{caminho.suffix}",
        content_disposition_type="inline",
    )

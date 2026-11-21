from datetime import date, datetime
from decimal import Decimal

import pytest

REGRA_CURSOS = 3

@pytest.fixture
def novo_aluno(client, dados_aluno):
    def _criar():
        resposta = client.post("/auth/cadastro-aluno", json=dados_aluno())
        assert resposta.status_code == 201, resposta.text
        return resposta.json()["id_aluno"]
    return _criar


@pytest.fixture
def nova_solicitacao():
    from app import models
    from app.database import SessionLocal

    def _criar(id_aluno, pontos=10, dia=date(2025, 3, 1), status="PENDENTE", created_at=None, pontos_aproveitados=None):
        db = SessionLocal()
        try:
            solicitacao = models.Solicitacao(
                id_aluno=id_aluno,
                id_regra_pontuacao=REGRA_CURSOS,
                descricao_atividade="Curso de teste",
                data_atividade=dia,
                ano=2025,
                semestre=1,
                quantidade=Decimal(str(pontos)),
                arquivo="teste.pdf",
                pontos_calculados=Decimal(str(pontos)),
                pontos_aproveitados=None if pontos_aproveitados is None else Decimal(str(pontos_aproveitados)),
                status=status,
            )
            if created_at:
                solicitacao.created_at = created_at
            db.add(solicitacao)
            db.commit()
            return solicitacao.id
        finally:
            db.close()
    return _criar


def listar(client, cabecalho, **filtros):
    resposta = client.get("/solicitacoes", params=filtros, headers=cabecalho)
    assert resposta.status_code == 200, resposta.text
    return resposta.json()


# ---------- Permissões ----------

def test_sem_token_recebe_401(client):
    assert client.get("/solicitacoes").status_code == 401
    assert client.patch("/solicitacoes/1/aprovar").status_code == 401
    assert client.patch("/solicitacoes/1/rejeitar", json={"observacao": "Motivo qualquer"}).status_code == 401


def test_aluno_recebe_403_nas_tres_rotas(client, cabecalho_aluno):
    assert client.get("/solicitacoes", headers=cabecalho_aluno).status_code == 403
    assert client.patch("/solicitacoes/1/aprovar", headers=cabecalho_aluno).status_code == 403
    assert client.patch("/solicitacoes/1/rejeitar", json={"observacao": "Motivo qualquer"}, headers=cabecalho_aluno).status_code == 403


def test_administrador_recebe_403(client, cabecalho_admin):
    assert client.get("/solicitacoes", headers=cabecalho_admin).status_code == 403


def test_professor_e_coordenador_listam(client, cabecalho_professor, cabecalho_coordenador):
    assert client.get("/solicitacoes", headers=cabecalho_professor).status_code == 200
    assert client.get("/solicitacoes", headers=cabecalho_coordenador).status_code == 200


# ---------- Listagem ----------

def test_lista_filtra_por_aluno_e_por_status(client, cabecalho_professor, novo_aluno, nova_solicitacao):
    aluno = novo_aluno()
    pendente = nova_solicitacao(aluno)
    aprovada = nova_solicitacao(aluno, status="APROVADA", pontos_aproveitados=10)
    nova_solicitacao(novo_aluno())

    todas = listar(client, cabecalho_professor, id_aluno=aluno)
    assert {s["id"] for s in todas} == {pendente, aprovada}

    so_pendentes = listar(client, cabecalho_professor, id_aluno=aluno, status="PENDENTE")
    assert [s["id"] for s in so_pendentes] == [pendente]


def test_lista_filtra_por_ppc(client, cabecalho_professor, novo_aluno, nova_solicitacao):
    aluno = novo_aluno()
    solicitacao = nova_solicitacao(aluno)

    assert solicitacao in {s["id"] for s in listar(client, cabecalho_professor, id_ppc=1, id_aluno=aluno)}
    assert listar(client, cabecalho_professor, id_ppc=999999, id_aluno=aluno) == []


def test_lista_das_mais_antigas_para_as_mais_novas(client, cabecalho_professor, novo_aluno, nova_solicitacao):
    aluno = novo_aluno()
    nova = nova_solicitacao(aluno, created_at=datetime(2025, 5, 1, 10, 0, 0))
    antiga = nova_solicitacao(aluno, created_at=datetime(2025, 3, 1, 10, 0, 0))
    meio = nova_solicitacao(aluno, created_at=datetime(2025, 4, 1, 10, 0, 0))

    ids = [s["id"] for s in listar(client, cabecalho_professor, id_aluno=aluno)]

    assert ids == [antiga, meio, nova]


def test_status_invalido_no_filtro_devolve_422(client, cabecalho_professor):
    resposta = client.get("/solicitacoes", params={"status": "QUALQUER"}, headers=cabecalho_professor)

    assert resposta.status_code == 422


# ---------- Aprovar ----------

def test_aprovar_grava_status_avaliador_observacao_e_pontos(client, cabecalho_professor, novo_aluno, nova_solicitacao):
    solicitacao = nova_solicitacao(novo_aluno(), pontos=15)
    id_professor = client.get("/me", headers=cabecalho_professor).json()["id"]

    resposta = client.patch(f"/solicitacoes/{solicitacao}/aprovar", json={"observacao": "Certificado conferido"}, headers=cabecalho_professor)

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["status"] == "APROVADA"
    assert corpo["avaliador"]["id"] == id_professor
    assert corpo["observacao"] == "Certificado conferido"
    assert corpo["pontos_aproveitados"] == 15


def test_aprovar_sem_corpo_funciona_e_deixa_observacao_vazia(client, cabecalho_coordenador, novo_aluno, nova_solicitacao):
    solicitacao = nova_solicitacao(novo_aluno(), pontos=5)

    resposta = client.patch(f"/solicitacoes/{solicitacao}/aprovar", headers=cabecalho_coordenador)

    assert resposta.status_code == 200
    assert resposta.json()["observacao"] is None
    assert resposta.json()["pontos_aproveitados"] == 5


def test_aprovar_respeita_o_limite_e_nao_depende_da_ordem(client, cabecalho_professor, novo_aluno, nova_solicitacao):
    aluno = novo_aluno()
    antiga = nova_solicitacao(aluno, pontos=30, dia=date(2025, 3, 1))
    recente = nova_solicitacao(aluno, pontos=30, dia=date(2025, 3, 20))

    primeira = client.patch(f"/solicitacoes/{recente}/aprovar", headers=cabecalho_professor)
    assert primeira.json()["pontos_aproveitados"] == 30

    segunda = client.patch(f"/solicitacoes/{antiga}/aprovar", headers=cabecalho_professor)
    assert segunda.json()["pontos_aproveitados"] == 30

    por_id = {s["id"]: s for s in listar(client, cabecalho_professor, id_aluno=aluno)}
    assert por_id[antiga]["pontos_aproveitados"] == 30
    assert por_id[recente]["pontos_aproveitados"] == 10


# ---------- Recusar ----------

def test_rejeitar_sem_motivo_valido_devolve_422(client, cabecalho_professor, novo_aluno, nova_solicitacao):
    aluno = novo_aluno()
    solicitacao = nova_solicitacao(aluno)

    for corpo in (None, {}, {"observacao": ""}, {"observacao": "   "}, {"observacao": "ok"}):
        resposta = client.patch(f"/solicitacoes/{solicitacao}/rejeitar", json=corpo, headers=cabecalho_professor)

        assert resposta.status_code == 422, corpo
        assert resposta.json()["detail"] == "Informe o motivo da recusa", corpo
    assert [s["status"] for s in listar(client, cabecalho_professor, id_aluno=aluno)] == ["PENDENTE"]


def test_rejeitar_aceita_motivo_de_3_a_1000_caracteres(client, cabecalho_professor, novo_aluno, nova_solicitacao):
    aluno = novo_aluno()
    curta = nova_solicitacao(aluno)
    longa = nova_solicitacao(aluno)

    assert client.patch(f"/solicitacoes/{curta}/rejeitar", json={"observacao": "abc"}, headers=cabecalho_professor).status_code == 200
    assert client.patch(f"/solicitacoes/{longa}/rejeitar", json={"observacao": "a" * 1000}, headers=cabecalho_professor).status_code == 200


def test_observacao_acima_de_1000_caracteres_devolve_422(client, cabecalho_professor, novo_aluno, nova_solicitacao):
    solicitacao = nova_solicitacao(novo_aluno())
    excesso = {"observacao": "a" * 1001}

    rejeitar = client.patch(f"/solicitacoes/{solicitacao}/rejeitar", json=excesso, headers=cabecalho_professor)
    aprovar = client.patch(f"/solicitacoes/{solicitacao}/aprovar", json=excesso, headers=cabecalho_professor)

    assert rejeitar.status_code == 422
    assert aprovar.status_code == 422
    assert aprovar.json()["detail"] == "A observação deve ter no máximo 1000 caracteres"


def test_aprovar_aceita_observacao_de_ate_1000_caracteres(client, cabecalho_professor, novo_aluno, nova_solicitacao):
    solicitacao = nova_solicitacao(novo_aluno())

    resposta = client.patch(f"/solicitacoes/{solicitacao}/aprovar", json={"observacao": "a" * 1000}, headers=cabecalho_professor)

    assert resposta.status_code == 200


def test_rejeitar_grava_status_avaliador_observacao_e_sem_pontos(client, cabecalho_coordenador, novo_aluno, nova_solicitacao):
    solicitacao = nova_solicitacao(novo_aluno(), pontos=12)
    id_coordenador = client.get("/me", headers=cabecalho_coordenador).json()["id"]

    resposta = client.patch(f"/solicitacoes/{solicitacao}/rejeitar", json={"observacao": "Certificado ilegível"}, headers=cabecalho_coordenador)

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["status"] == "REJEITADA"
    assert corpo["avaliador"]["id"] == id_coordenador
    assert corpo["observacao"] == "Certificado ilegível"
    assert corpo["pontos_aproveitados"] is None


def test_rejeitar_recalcula_as_outras_do_aluno(client, cabecalho_professor, novo_aluno, nova_solicitacao):
    aluno = novo_aluno()
    desatualizada = nova_solicitacao(aluno, pontos=30, status="APROVADA", pontos_aproveitados=5)
    pendente = nova_solicitacao(aluno, pontos=10)

    resposta = client.patch(f"/solicitacoes/{pendente}/rejeitar", json={"observacao": "Fora do prazo"}, headers=cabecalho_professor)

    assert resposta.status_code == 200
    por_id = {s["id"]: s for s in listar(client, cabecalho_professor, id_aluno=aluno)}
    assert por_id[desatualizada]["pontos_aproveitados"] == 30
    assert por_id[pendente]["pontos_aproveitados"] is None


# ---------- Já avaliada

def test_avaliar_de_novo_devolve_409(client, cabecalho_professor, novo_aluno, nova_solicitacao):
    aprovada = nova_solicitacao(novo_aluno())
    rejeitada = nova_solicitacao(novo_aluno())
    client.patch(f"/solicitacoes/{aprovada}/aprovar", headers=cabecalho_professor)
    client.patch(f"/solicitacoes/{rejeitada}/rejeitar", json={"observacao": "Sem comprovante"}, headers=cabecalho_professor)

    for id_solicitacao in (aprovada, rejeitada):
        de_novo = [
            client.patch(f"/solicitacoes/{id_solicitacao}/aprovar", headers=cabecalho_professor),
            client.patch(f"/solicitacoes/{id_solicitacao}/rejeitar", json={"observacao": "Motivo qualquer"}, headers=cabecalho_professor),
        ]
        for resposta in de_novo:
            assert resposta.status_code == 409
            assert resposta.json()["detail"] == "Solicitação já avaliada"


def test_solicitacao_inexistente_devolve_404(client, cabecalho_professor):
    assert client.patch("/solicitacoes/999999/aprovar", headers=cabecalho_professor).status_code == 404
    assert client.patch("/solicitacoes/999999/rejeitar", json={"observacao": "Motivo qualquer"}, headers=cabecalho_professor).status_code == 404
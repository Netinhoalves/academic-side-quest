import uuid
from datetime import date
from decimal import Decimal

import pytest

from app import models
from app.alunos import calcular_percentual
from app.database import SessionLocal

CAMPOS_DO_ALUNO = {
    "id", "id_usuario", "nome", "email", "matricula", "data_ingresso", "curso", "ppc",
    "total_exigido", "total_aproveitado", "percentual", "pendentes",
}


@pytest.fixture
def novo_aluno(client, entrar, dados_aluno):
    """Cadastra um aluno novo e devolve o id da tabela Aluno, o cabeçalho de login e os dados usados."""
    def _criar(**extra):
        dados = dados_aluno(**extra)
        resposta = client.post("/auth/cadastro-aluno", json=dados)
        assert resposta.status_code == 201, resposta.text
        return resposta.json()["id_aluno"], entrar(dados["email"], dados["senha"]), dados
    return _criar


def gravar_solicitacao(id_aluno, regra, dia, status, calculados, aproveitados=None):
    """Grava a solicitação direto no banco, já avaliada: a rota de aprovar é da TASK-58."""
    with SessionLocal() as db:
        solicitacao = models.Solicitacao(
            id_aluno=id_aluno,
            id_regra_pontuacao=regra,
            descricao_atividade="Atividade de teste",
            data_atividade=dia,
            ano=dia.year,
            semestre=1 if dia.month <= 6 else 2,
            arquivo="teste.pdf",
            pontos_calculados=Decimal(str(calculados)),
            pontos_aproveitados=None if aproveitados is None else Decimal(str(aproveitados)),
            status=status,
        )
        db.add(solicitacao)
        db.commit()
        return solicitacao.id


def gravar_exemplo_do_contrato(id_aluno):
    """As 4 solicitações do exemplo do contrato: 2 aprovadas (15 + 15), 1 pendente e 1 recusada."""
    return [
        gravar_solicitacao(id_aluno, 3, date(2026, 6, 10), "APROVADA", 15, 15),
        gravar_solicitacao(id_aluno, 5, date(2026, 8, 18), "APROVADA", 15, 15),
        gravar_solicitacao(id_aluno, 18, date(2026, 9, 1), "PENDENTE", 30),
        gravar_solicitacao(id_aluno, 12, date(2026, 10, 7), "REJEITADA", 3),
    ]


def por_id(itens):
    return {item["id"]: item for item in itens}


@pytest.mark.parametrize(
    "aproveitado, exigido, percentual",
    [
        ("30", "275", "10.91"),
        ("0", "275", "0.00"),
        ("7.5", "275", "2.73"),
        ("2", "3", "66.67"),
        ("275", "275", "100.00"),
        ("300", "275", "100.00"),  # nunca passa de 100
    ],
)
def test_calcular_percentual(aproveitado, exigido, percentual):
    assert calcular_percentual(Decimal(aproveitado), Decimal(exigido)) == Decimal(percentual)


# Progresso do aluno (GET /alunos/me/progresso)

def test_aluno_sem_solicitacoes_tem_o_progresso_zerado(client, novo_aluno):
    _, cabecalho, _ = novo_aluno()

    resposta = client.get("/alunos/me/progresso", headers=cabecalho)

    assert resposta.status_code == 200
    progresso = resposta.json()
    assert (progresso["total_exigido"], progresso["total_aproveitado"], progresso["percentual"], progresso["pendentes"]) == (275, 0, 0, 0)
    # Vêm todas as categorias e subcategorias do PPC, mesmo sem pontos, com os limites ao lado
    assert [categoria["id"] for categoria in progresso["categorias"]] == [1, 2, 3, 4]
    assert sum(len(categoria["subcategorias"]) for categoria in progresso["categorias"]) == 18
    categoria_1 = progresso["categorias"][0]
    assert (categoria_1["limite_total"], categoria_1["limite_semestre"], categoria_1["aproveitado_total"], categoria_1["semestres"]) == (120, 80, 0, [])
    subcategoria_1_3 = por_id(categoria_1["subcategorias"])[3]
    assert subcategoria_1_3 == {
        "id": 3,
        "codigo": "1.3",
        "nome": "Realização de cursos de língua estrangeira, informática e outros de formação cultural, social ou específica do âmbito do curso",
        "limite_semestre": 40,
        "aproveitado_total": 0,
        "semestres": [],
    }


def test_progresso_do_exemplo_do_contrato(client, novo_aluno):
    id_aluno, cabecalho, _ = novo_aluno()
    gravar_exemplo_do_contrato(id_aluno)

    progresso = client.get("/alunos/me/progresso", headers=cabecalho).json()

    # Só as aprovadas contam: 15 + 15 = 30 de 275; a pendente entra na contagem; a recusada não conta
    assert (progresso["total_aproveitado"], progresso["percentual"], progresso["pendentes"]) == (30, 10.91, 1)
    categorias = por_id(progresso["categorias"])
    assert categorias[1]["aproveitado_total"] == 15
    assert categorias[1]["semestres"] == [{"ano": 2026, "semestre": 1, "aproveitado": 15}]
    assert por_id(categorias[1]["subcategorias"])[3]["semestres"] == [{"ano": 2026, "semestre": 1, "aproveitado": 15}]
    assert categorias[2]["semestres"] == [{"ano": 2026, "semestre": 2, "aproveitado": 15}]
    assert por_id(categorias[2]["subcategorias"])[5]["aproveitado_total"] == 15
    assert (categorias[3]["aproveitado_total"], categorias[3]["semestres"]) == (0, [])
    assert por_id(categorias[3]["subcategorias"])[10]["aproveitado_total"] == 0
    assert (categorias[4]["aproveitado_total"], categorias[4]["semestres"]) == (0, [])


def test_progresso_separa_os_semestres(client, novo_aluno):
    id_aluno, cabecalho, _ = novo_aluno()
    gravar_solicitacao(id_aluno, 3, date(2025, 9, 10), "APROVADA", 20, 20)
    gravar_solicitacao(id_aluno, 3, date(2026, 3, 10), "APROVADA", 25, 25)
    gravar_solicitacao(id_aluno, 1, date(2026, 3, 12), "APROVADA", 5, 5)
    # Aprovada sem pontos (limite já atingido): não cria semestre
    gravar_solicitacao(id_aluno, 1, date(2026, 8, 1), "APROVADA", 5, 0)

    progresso = client.get("/alunos/me/progresso", headers=cabecalho).json()

    categoria_1 = por_id(progresso["categorias"])[1]
    assert categoria_1["aproveitado_total"] == 50
    assert categoria_1["semestres"] == [
        {"ano": 2025, "semestre": 2, "aproveitado": 20},
        {"ano": 2026, "semestre": 1, "aproveitado": 30},
    ]
    subcategorias = por_id(categoria_1["subcategorias"])
    assert subcategorias[3]["semestres"] == [
        {"ano": 2025, "semestre": 2, "aproveitado": 20},
        {"ano": 2026, "semestre": 1, "aproveitado": 25},
    ]
    assert (subcategorias[1]["aproveitado_total"], subcategorias[1]["semestres"]) == (5, [{"ano": 2026, "semestre": 1, "aproveitado": 5}])
    assert (progresso["total_aproveitado"], progresso["percentual"]) == (50, 18.18)


def test_progresso_usa_o_ppc_do_aluno(client, cabecalho_coordenador, ppc_valido, novo_aluno):
    outro_ppc = client.post("/ppcs", json=ppc_valido(), headers=cabecalho_coordenador)
    assert outro_ppc.status_code == 201, outro_ppc.text
    _, cabecalho, _ = novo_aluno(id_ppc=outro_ppc.json()["id"])

    progresso = client.get("/alunos/me/progresso", headers=cabecalho).json()

    assert progresso["total_exigido"] == 100
    assert [categoria["nome"] for categoria in progresso["categorias"]] == ["Atividades de teste"]
    assert progresso["categorias"][0]["subcategorias"][0]["limite_semestre"] == 30


@pytest.mark.parametrize("cabecalho", ["cabecalho_professor", "cabecalho_coordenador", "cabecalho_admin"])
def test_so_o_aluno_ve_o_proprio_progresso(request, client, cabecalho):
    resposta = client.get("/alunos/me/progresso", headers=request.getfixturevalue(cabecalho))

    assert resposta.status_code == 403
    assert resposta.json()["detail"] == "Acesso negado: recurso restrito a usuários com perfil Aluno"


def test_progresso_sem_token_devolve_401(client):
    assert client.get("/alunos/me/progresso").status_code == 401


# Lista de alunos (GET /alunos)

@pytest.mark.parametrize("cabecalho", ["cabecalho_professor", "cabecalho_coordenador"])
def test_professor_e_coordenador_veem_a_lista(request, client, novo_aluno, cabecalho):
    marca = uuid.uuid4().hex[:8]
    id_aluno, _, dados = novo_aluno(nome=f"Aluna {marca}")
    gravar_exemplo_do_contrato(id_aluno)

    resposta = client.get("/alunos", params={"busca": marca}, headers=request.getfixturevalue(cabecalho))

    assert resposta.status_code == 200
    assert len(resposta.json()) == 1
    aluno = resposta.json()[0]
    assert set(aluno) == CAMPOS_DO_ALUNO
    assert (aluno["id"], aluno["nome"], aluno["email"], aluno["matricula"]) == (id_aluno, dados["nome"], dados["email"], dados["matricula"])
    assert aluno["curso"] == {"id": 1, "nome": "Tecnologia em Análise e Desenvolvimento de Sistemas", "sigla": "TADS", "instituicao": "IFMS - Campus Três Lagoas", "ativo": True}
    assert aluno["ppc"] == {"id": 1, "nome": "PPC TADS 2019", "ano": 2019}
    assert (aluno["total_exigido"], aluno["total_aproveitado"], aluno["percentual"], aluno["pendentes"]) == (275, 30, 10.91, 1)


def test_lista_em_ordem_alfabetica(client, cabecalho_professor, novo_aluno):
    marca = uuid.uuid4().hex[:8]
    for nome in ("Zeca", "ana", "Bruno"):
        novo_aluno(nome=f"{nome} {marca}")

    resposta = client.get("/alunos", params={"busca": marca}, headers=cabecalho_professor)

    assert [aluno["nome"] for aluno in resposta.json()] == [f"ana {marca}", f"Bruno {marca}", f"Zeca {marca}"]


def test_busca_por_nome_ou_matricula_sem_diferenciar_maiusculas(client, cabecalho_professor, novo_aluno):
    marca = uuid.uuid4().hex[:8]
    id_aluno, _, dados = novo_aluno(nome=f"Carla Busca {marca}")

    por_nome = client.get("/alunos", params={"busca": f"carla busca {marca}".upper()}, headers=cabecalho_professor)
    por_matricula = client.get("/alunos", params={"busca": dados["matricula"].lower()}, headers=cabecalho_professor)
    sem_resultado = client.get("/alunos", params={"busca": f"ninguem-{marca}"}, headers=cabecalho_professor)

    assert [aluno["id"] for aluno in por_nome.json()] == [id_aluno]
    assert [aluno["id"] for aluno in por_matricula.json()] == [id_aluno]
    assert sem_resultado.json() == []


def test_filtro_por_ppc(client, cabecalho_coordenador, ppc_valido, novo_aluno):
    marca = uuid.uuid4().hex[:8]
    outro_ppc = client.post("/ppcs", json=ppc_valido(), headers=cabecalho_coordenador).json()
    id_no_outro, _, _ = novo_aluno(nome=f"Outro PPC {marca}", id_ppc=outro_ppc["id"])
    id_no_tads, _, _ = novo_aluno(nome=f"TADS {marca}")

    do_outro = client.get("/alunos", params={"id_ppc": outro_ppc["id"]}, headers=cabecalho_coordenador)
    do_tads = client.get("/alunos", params={"id_ppc": 1, "busca": marca}, headers=cabecalho_coordenador)

    assert [aluno["id"] for aluno in do_outro.json()] == [id_no_outro]
    assert do_outro.json()[0]["total_exigido"] == 100
    assert [aluno["id"] for aluno in do_tads.json()] == [id_no_tads]


@pytest.mark.parametrize("cabecalho", ["cabecalho_aluno", "cabecalho_admin"])
def test_aluno_e_admin_nao_veem_a_lista(request, client, cabecalho):
    resposta = client.get("/alunos", headers=request.getfixturevalue(cabecalho))

    assert resposta.status_code == 403
    assert resposta.json()["detail"] == "Acesso negado: recurso restrito a usuários com perfil Professor ou Coordenador"


# Detalhe do aluno (GET /alunos/{id})

def test_detalhe_do_aluno(client, cabecalho_professor, novo_aluno):
    id_aluno, cabecalho, dados = novo_aluno()
    ids = gravar_exemplo_do_contrato(id_aluno)

    resposta = client.get(f"/alunos/{id_aluno}", headers=cabecalho_professor)

    assert resposta.status_code == 200
    detalhe = resposta.json()
    assert set(detalhe) == {"aluno", "progresso", "solicitacoes"}
    assert set(detalhe["aluno"]) == CAMPOS_DO_ALUNO
    assert (detalhe["aluno"]["id"], detalhe["aluno"]["nome"], detalhe["aluno"]["percentual"]) == (id_aluno, dados["nome"], 10.91)
    # O mesmo progresso que o aluno vê
    assert detalhe["progresso"] == client.get("/alunos/me/progresso", headers=cabecalho).json()
    # As solicitações como no GET /alunos/me/solicitacoes: da atividade mais recente para a mais antiga
    assert [solicitacao["id"] for solicitacao in detalhe["solicitacoes"]] == list(reversed(ids))
    assert detalhe["solicitacoes"] == client.get("/alunos/me/solicitacoes", headers=cabecalho).json()


def test_detalhe_de_aluno_que_nao_existe_devolve_404(client, cabecalho_coordenador):
    resposta = client.get("/alunos/999999", headers=cabecalho_coordenador)

    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Aluno não encontrado"


def test_aluno_nao_ve_o_detalhe_de_outro_aluno(client, cabecalho_aluno, novo_aluno):
    id_aluno, _, _ = novo_aluno()

    resposta = client.get(f"/alunos/{id_aluno}", headers=cabecalho_aluno)

    assert resposta.status_code == 403

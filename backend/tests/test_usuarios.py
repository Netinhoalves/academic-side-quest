import threading

import pytest


@pytest.mark.parametrize(
    "quem, id_perfil, esperado",
    [
        ("admin", 3, 201),
        ("admin", 2, 201),
        ("admin", 4, 403),
        ("admin", 1, 403),
        ("coordenador", 2, 201),
        ("coordenador", 3, 403),
    ],
)
def test_quem_pode_cadastrar_quem(client, request, dados_servidor, quem, id_perfil, esperado):
    cabecalho = request.getfixturevalue(f"cabecalho_{quem}")

    resposta = client.post("/usuarios", json=dados_servidor(id_perfil=id_perfil), headers=cabecalho)

    assert resposta.status_code == esperado


@pytest.mark.parametrize(
    "campo, valor",
    [
        ("senha", "x" * 73),
        ("senha", "123"),
        ("nome", "N" * 151),
        ("nome", "   "),
        ("email", "sem-arroba"),
    ],
)
def test_cadastro_de_servidor_com_dado_invalido_devolve_422(client, cabecalho_admin, dados_servidor, campo, valor):
    resposta = client.post("/usuarios", json=dados_servidor(**{campo: valor}), headers=cabecalho_admin)

    assert resposta.status_code == 422


def test_cadastros_simultaneos_iguais_devolvem_409_e_nao_500(client, cabecalho_admin, dados_servidor):
    dados = dados_servidor()
    respostas = []

    def cadastrar():
        respostas.append(client.post("/usuarios", json=dados, headers=cabecalho_admin).status_code)

    threads = [threading.Thread(target=cadastrar) for _ in range(5)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert sorted(respostas) == [201, 409, 409, 409, 409]


def test_matricula_em_branco_vira_null(client, cabecalho_admin, dados_servidor):
    for _ in range(2):
        resposta = client.post("/usuarios", json=dados_servidor(matricula=""), headers=cabecalho_admin)

        assert resposta.status_code == 201
        assert resposta.json()["matricula"] is None


def test_email_do_servidor_e_salvo_em_minusculas(client, cabecalho_admin, dados_servidor):
    dados = dados_servidor()
    dados["email"] = dados["email"].upper()

    resposta = client.post("/usuarios", json=dados, headers=cabecalho_admin)

    assert resposta.status_code == 201
    assert resposta.json()["email"] == dados["email"].lower()


@pytest.mark.parametrize("campo", ["nome", "email", "senha", "id_perfil", "ativo"])
def test_put_com_null_devolve_422(client, cabecalho_admin, novo_servidor, campo):
    servidor = novo_servidor()

    resposta = client.put(f"/usuarios/{servidor['id']}", json={campo: None}, headers=cabecalho_admin)

    assert resposta.status_code == 422


@pytest.mark.parametrize("corpo", [{"ativo": False}, {"id_perfil": 2}])
def test_admin_nao_pode_se_desativar_nem_trocar_o_proprio_perfil(client, cabecalho_admin, corpo):
    eu = client.get("/me", headers=cabecalho_admin).json()

    resposta = client.put(f"/usuarios/{eu['id']}", json=corpo, headers=cabecalho_admin)

    assert resposta.status_code == 400


def test_edicao_pelo_painel_com_matricula_null_continua_funcionando(client, cabecalho_admin):
    """O painel manda nome, e-mail, matrícula, perfil e ativo; o admin do seed não tem matrícula."""
    eu = client.get("/me", headers=cabecalho_admin).json()
    corpo = {"nome": eu["nome"], "email": eu["email"], "matricula": None, "id_perfil": 4, "ativo": True}

    resposta = client.put(f"/usuarios/{eu['id']}", json=corpo, headers=cabecalho_admin)

    assert resposta.status_code == 200

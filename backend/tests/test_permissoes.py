def test_aluno_criando_ppc_recebe_403(client, cabecalho_aluno, ppc_valido):
    resposta = client.post("/ppcs", json=ppc_valido(), headers=cabecalho_aluno)

    assert resposta.status_code == 403


def test_professor_criando_ppc_recebe_403(client, cabecalho_professor, ppc_valido):
    resposta = client.post("/ppcs", json=ppc_valido(), headers=cabecalho_professor)

    assert resposta.status_code == 403


def test_criar_ppc_sem_token_recebe_401(client, ppc_valido):
    resposta = client.post("/ppcs", json=ppc_valido())

    assert resposta.status_code == 401


def test_coordenador_criando_ppc_recebe_201(client, cabecalho_coordenador, ppc_valido):
    resposta = client.post("/ppcs", json=ppc_valido(), headers=cabecalho_coordenador)

    assert resposta.status_code == 201

def test_cadastro_de_aluno_com_sucesso(client, dados_aluno):
    dados = dados_aluno()

    resposta = client.post("/auth/cadastro-aluno", json=dados)

    assert resposta.status_code == 201
    assert resposta.json()["perfil"] == "Aluno"
    assert resposta.json()["id_ppc"] == 1
    login = client.post("/login", json={"email": dados["email"], "senha": dados["senha"]})
    assert login.status_code == 200


def test_cadastro_com_email_repetido_devolve_409(client, dados_aluno):
    resposta = client.post("/auth/cadastro-aluno", json=dados_aluno(email="aluno@teste.com"))

    assert resposta.status_code == 409
    assert resposta.json()["detail"] == "E-mail já cadastrado"


def test_cadastro_com_matricula_repetida_devolve_409(client, dados_aluno):
    resposta = client.post("/auth/cadastro-aluno", json=dados_aluno(matricula="2023000001"))

    assert resposta.status_code == 409
    assert resposta.json()["detail"] == "Matrícula já cadastrada"


def test_id_perfil_de_admin_no_cadastro_e_ignorado(client, dados_aluno):
    dados = dados_aluno(id_perfil=4)

    resposta = client.post("/auth/cadastro-aluno", json=dados)

    assert resposta.status_code == 201
    assert resposta.json()["perfil"] == "Aluno"
    token = client.post("/login", json={"email": dados["email"], "senha": dados["senha"]}).json()["token"]
    me = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert me.json()["perfil"] == "Aluno"


def test_cadastro_com_ppc_que_nao_existe_devolve_400(client, dados_aluno):
    resposta = client.post("/auth/cadastro-aluno", json=dados_aluno(id_ppc=9999))

    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "PPC não encontrado"


def test_cadastro_com_senha_curta_devolve_422(client, dados_aluno):
    resposta = client.post("/auth/cadastro-aluno", json=dados_aluno(senha="123"))

    assert resposta.status_code == 422
    assert resposta.json()["detail"][0]["msg"] == "A senha deve ter pelo menos 6 caracteres"

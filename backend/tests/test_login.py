def test_login_com_dados_certos_devolve_token(client):
    resposta = client.post("/login", json={"email": "admin@teste.com", "senha": "admin123"})

    assert resposta.status_code == 200
    token = resposta.json()["token"]
    me = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["perfil"] == "Administrador"


def test_login_com_senha_errada_devolve_401(client):
    resposta = client.post("/login", json={"email": "admin@teste.com", "senha": "senha-errada"})

    assert resposta.status_code == 401
    assert resposta.json()["detail"] == "E-mail ou senha inválidos"


def test_login_com_email_que_nao_existe_devolve_a_mesma_mensagem(client):
    resposta = client.post("/login", json={"email": "ninguem@teste.local", "senha": "123456"})

    assert resposta.status_code == 401
    assert resposta.json()["detail"] == "E-mail ou senha inválidos"


def test_login_de_usuario_inativo_devolve_401(client, cabecalho_admin, novo_servidor):
    servidor = novo_servidor()
    desativar = client.delete(f"/usuarios/{servidor['id']}", headers=cabecalho_admin)
    assert desativar.status_code == 204

    resposta = client.post("/login", json={"email": servidor["email"], "senha": servidor["senha"]})

    assert resposta.status_code == 401
    assert resposta.json()["detail"].startswith("Usuário inativo")

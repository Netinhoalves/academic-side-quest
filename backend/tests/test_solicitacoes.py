import re
from datetime import date, timedelta

import pytest

from app.solicitacoes import TAMANHO_MAXIMO, seis_meses_antes

PDF = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF\n"
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32
JPG = b"\xff\xd8\xff\xe0" + b"\x00" * 32


@pytest.fixture(autouse=True)
def pasta(tmp_path, monkeypatch):
    """Cada teste grava os comprovantes numa pasta temporária, nunca na backend/uploads."""
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path))
    return tmp_path


@pytest.fixture
def novo_aluno(client, entrar, dados_aluno):
    """Cadastra um aluno novo e devolve o cabeçalho de login dele: cada teste começa sem solicitações."""
    def _criar():
        dados = dados_aluno()
        resposta = client.post("/auth/cadastro-aluno", json=dados)
        assert resposta.status_code == 201, resposta.text
        return entrar(dados["email"], dados["senha"])
    return _criar


@pytest.fixture
def enviar(client):
    """Envia uma solicitação como o front envia (multipart). Por padrão: 15 horas na regra 3, com um PDF."""
    def _enviar(cabecalho, arquivo=("certificado.pdf", PDF, "application/pdf"), **campos):
        dados = {
            "id_regra_pontuacao": "3",
            "descricao_atividade": "Curso online de Python",
            "data_atividade": str(date.today() - timedelta(days=10)),
            "quantidade": "15",
        }
        dados.update(campos)
        dados = {campo: valor for campo, valor in dados.items() if valor is not None}
        return client.post("/solicitacoes", data=dados, files={"arquivo": arquivo}, headers=cabecalho)
    return _enviar


# Envio (POST /solicitacoes)

def test_aluno_envia_atividade_e_recebe_a_solicitacao_pendente(client, novo_aluno, enviar, pasta):
    cabecalho = novo_aluno()
    dia = date.today() - timedelta(days=10)

    resposta = enviar(cabecalho, data_atividade=str(dia))

    assert resposta.status_code == 201, resposta.text
    corpo = resposta.json()
    assert corpo["status"] == "PENDENTE"
    assert corpo["quantidade"] == 15
    assert corpo["pontos_calculados"] == 15
    assert corpo["pontos_aproveitados"] is None
    assert corpo["avaliador"] is None
    assert corpo["observacao"] is None
    assert corpo["data_atividade"] == str(dia)
    assert corpo["ano"] == dia.year
    assert corpo["semestre"] == (1 if dia.month <= 6 else 2)
    assert corpo["descricao_atividade"] == "Curso online de Python"
    assert corpo["regra"] == {"id": 3, "titulo_exibicao": "1 ponto por hora", "tipo": "hora", "multiplicador": 1, "operacao": "MULTIPLICACAO"}
    assert corpo["subcategoria"]["codigo"] == "1.3"
    assert corpo["categoria"] == {"id": 1, "nome": "Atividades de aperfeiçoamento e enriquecimento cultural e esportivo"}
    me = client.get("/me", headers=cabecalho).json()
    assert corpo["aluno"]["nome"] == me["nome"]
    assert corpo["aluno"]["matricula"] == me["matricula"]
    # O caminho do arquivo no servidor não sai na resposta
    assert "arquivo" not in corpo
    salvos = list(pasta.iterdir())
    assert len(salvos) == 1
    assert salvos[0].read_bytes() == PDF


def test_regra_soma_vale_o_valor_fixo_e_ignora_a_quantidade(novo_aluno, enviar):
    resposta = enviar(novo_aluno(), id_regra_pontuacao="5", quantidade="7")

    assert resposta.status_code == 201, resposta.text
    assert resposta.json()["quantidade"] is None
    assert resposta.json()["pontos_calculados"] == 15


def test_regra_soma_sem_quantidade_e_aceita(novo_aluno, enviar):
    resposta = enviar(novo_aluno(), id_regra_pontuacao="5", quantidade=None)

    assert resposta.status_code == 201, resposta.text
    assert resposta.json()["pontos_calculados"] == 15


@pytest.mark.parametrize(
    "regra, quantidade, pontos",
    [
        ("18", "4", 30),       # 7,5 pontos por mês x 4 meses
        ("3", "1.5", 1.5),     # 1 ponto por hora x 1,5 hora
        ("18", "2.15", 16.13), # 16,125 arredonda para 16,13
    ],
)
def test_regra_multiplicacao_multiplica_pela_quantidade(novo_aluno, enviar, regra, quantidade, pontos):
    resposta = enviar(novo_aluno(), id_regra_pontuacao=regra, quantidade=quantidade)

    assert resposta.status_code == 201, resposta.text
    assert resposta.json()["pontos_calculados"] == pontos


def test_regra_multiplicacao_sem_quantidade_devolve_422(novo_aluno, enviar, pasta):
    resposta = enviar(novo_aluno(), quantidade=None)

    assert resposta.status_code == 422
    assert resposta.json()["detail"] == "Informe a quantidade"
    assert list(pasta.iterdir()) == []


@pytest.mark.parametrize("quantidade", ["0", "-2", "10000.01", "1.234"])
def test_quantidade_invalida_devolve_422(novo_aluno, enviar, quantidade):
    resposta = enviar(novo_aluno(), quantidade=quantidade)

    assert resposta.status_code == 422
    assert resposta.json()["detail"] == "A quantidade deve ser maior que zero, até 10000, com no máximo 2 casas decimais"


@pytest.mark.parametrize("quantidade", ["abc", "NaN", "Infinity"])
def test_quantidade_que_nao_e_numero_devolve_422(novo_aluno, enviar, quantidade):
    resposta = enviar(novo_aluno(), quantidade=quantidade)

    assert resposta.status_code == 422


@pytest.mark.parametrize("id_regra", ["9999", "regra-do-outro-ppc"])
def test_regra_que_nao_existe_ou_de_outro_ppc_devolve_400(client, cabecalho_coordenador, ppc_valido, novo_aluno, enviar, id_regra):
    if id_regra == "regra-do-outro-ppc":
        outro_ppc = client.post("/ppcs", json=ppc_valido(), headers=cabecalho_coordenador)
        assert outro_ppc.status_code == 201, outro_ppc.text
        id_regra = str(outro_ppc.json()["categorias"][0]["subcategorias"][0]["regras"][0]["id"])

    resposta = enviar(novo_aluno(), id_regra_pontuacao=id_regra)

    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "A regra não pertence ao PPC do aluno"


@pytest.mark.parametrize("descricao", ["ab", "     ", "a" * 501])
def test_descricao_curta_vazia_ou_longa_devolve_422(novo_aluno, enviar, descricao):
    resposta = enviar(novo_aluno(), descricao_atividade=descricao)

    assert resposta.status_code == 422
    assert resposta.json()["detail"] == "A descrição da atividade deve ter de 3 a 500 caracteres"


def test_data_futura_devolve_422(novo_aluno, enviar, pasta):
    resposta = enviar(novo_aluno(), data_atividade=str(date.today() + timedelta(days=1)))

    assert resposta.status_code == 422
    assert resposta.json()["detail"] == "A data da atividade não pode ser futura"
    assert list(pasta.iterdir()) == []


def test_data_com_mais_de_6_meses_devolve_422(novo_aluno, enviar):
    resposta = enviar(novo_aluno(), data_atividade=str(seis_meses_antes(date.today()) - timedelta(days=1)))

    assert resposta.status_code == 422
    assert resposta.json()["detail"] == "A atividade deve ter sido realizada nos últimos 6 meses"


@pytest.mark.parametrize("dia", ["hoje", "limite"])
def test_data_de_hoje_e_de_exatos_6_meses_sao_aceitas(novo_aluno, enviar, dia):
    hoje = date.today()
    data_atividade = hoje if dia == "hoje" else seis_meses_antes(hoje)

    resposta = enviar(novo_aluno(), data_atividade=str(data_atividade))

    assert resposta.status_code == 201, resposta.text


@pytest.mark.parametrize(
    "hoje, limite",
    [
        (date(2026, 11, 4), date(2026, 5, 4)),
        (date(2026, 3, 15), date(2025, 9, 15)),
        (date(2026, 6, 30), date(2025, 12, 30)),
        (date(2026, 8, 31), date(2026, 2, 28)),  # fevereiro não tem dia 31
        (date(2028, 8, 31), date(2028, 2, 29)),  # ano bissexto
        (date(2026, 12, 31), date(2026, 6, 30)),
    ],
)
def test_seis_meses_antes(hoje, limite):
    assert seis_meses_antes(hoje) == limite


def test_arquivo_maior_que_5_mb_devolve_413(novo_aluno, enviar, pasta):
    grande = PDF + b"0" * TAMANHO_MAXIMO

    resposta = enviar(novo_aluno(), arquivo=("certificado.pdf", grande, "application/pdf"))

    assert resposta.status_code == 413
    assert resposta.json()["detail"] == "O arquivo deve ter no máximo 5 MB"
    assert list(pasta.iterdir()) == []


def test_arquivo_de_exatos_5_mb_e_aceito(novo_aluno, enviar):
    no_limite = PDF + b"0" * (TAMANHO_MAXIMO - len(PDF))

    resposta = enviar(novo_aluno(), arquivo=("certificado.pdf", no_limite, "application/pdf"))

    assert resposta.status_code == 201, resposta.text


@pytest.mark.parametrize(
    "conteudo",
    [
        b"",
        b"so um texto com o nome de pdf",
        b"<html><script>alert(1)</script></html>",
        b"MZ\x90\x00 executavel do Windows",
    ],
)
def test_arquivo_que_nao_e_pdf_jpg_ou_png_devolve_422(novo_aluno, enviar, pasta, conteudo):
    resposta = enviar(novo_aluno(), arquivo=("certificado.pdf", conteudo, "application/pdf"))

    assert resposta.status_code == 422
    assert resposta.json()["detail"] == "O arquivo deve ser PDF, JPG ou PNG"
    assert list(pasta.iterdir()) == []


def test_sem_arquivo_devolve_422(client, novo_aluno):
    dados = {"id_regra_pontuacao": "3", "descricao_atividade": "Curso", "data_atividade": str(date.today()), "quantidade": "1"}

    resposta = client.post("/solicitacoes", data=dados, headers=novo_aluno())

    assert resposta.status_code == 422


def test_nome_do_arquivo_enviado_nao_entra_no_caminho(novo_aluno, enviar, pasta):
    resposta = enviar(novo_aluno(), arquivo=("../../../etc/certificado.pdf", PDF, "application/pdf"))

    assert resposta.status_code == 201, resposta.text
    salvos = list(pasta.iterdir())
    assert len(salvos) == 1
    assert re.fullmatch(r"[0-9a-f]{32}\.pdf", salvos[0].name)


@pytest.mark.parametrize("cabecalho", ["cabecalho_professor", "cabecalho_coordenador", "cabecalho_admin"])
def test_quem_nao_e_aluno_nao_envia_solicitacao(request, enviar, cabecalho):
    resposta = enviar(request.getfixturevalue(cabecalho))

    assert resposta.status_code == 403
    assert resposta.json()["detail"] == "Acesso negado: recurso restrito a usuários com perfil Aluno"


def test_envio_sem_token_devolve_401(enviar):
    assert enviar({}).status_code == 401


# Lista do aluno (GET /alunos/me/solicitacoes)

def test_aluno_ve_as_proprias_solicitacoes_da_mais_recente_para_a_mais_antiga(client, novo_aluno, cabecalho_aluno, enviar):
    cabecalho = novo_aluno()
    hoje = date.today()
    ids = {}
    for dias in (30, 2, 15):
        resposta = enviar(cabecalho, data_atividade=str(hoje - timedelta(days=dias)), descricao_atividade=f"Atividade de {dias} dias atrás")
        assert resposta.status_code == 201, resposta.text
        ids[dias] = resposta.json()["id"]
    de_outro_aluno = enviar(cabecalho_aluno).json()["id"]

    resposta = client.get("/alunos/me/solicitacoes", headers=cabecalho)

    assert resposta.status_code == 200
    assert [solicitacao["id"] for solicitacao in resposta.json()] == [ids[2], ids[15], ids[30]]
    assert de_outro_aluno not in [solicitacao["id"] for solicitacao in resposta.json()]


def test_filtro_por_status(client, novo_aluno, enviar):
    cabecalho = novo_aluno()
    id_solicitacao = enviar(cabecalho).json()["id"]

    pendentes = client.get("/alunos/me/solicitacoes", params={"status": "PENDENTE"}, headers=cabecalho)
    aprovadas = client.get("/alunos/me/solicitacoes", params={"status": "APROVADA"}, headers=cabecalho)
    invalido = client.get("/alunos/me/solicitacoes", params={"status": "QUALQUER"}, headers=cabecalho)

    assert [solicitacao["id"] for solicitacao in pendentes.json()] == [id_solicitacao]
    assert aprovadas.json() == []
    assert invalido.status_code == 422


def test_aluno_sem_solicitacoes_recebe_lista_vazia(client, novo_aluno):
    resposta = client.get("/alunos/me/solicitacoes", headers=novo_aluno())

    assert resposta.status_code == 200
    assert resposta.json() == []


def test_professor_nao_usa_a_lista_do_aluno(client, cabecalho_professor):
    resposta = client.get("/alunos/me/solicitacoes", headers=cabecalho_professor)

    assert resposta.status_code == 403


# Comprovante (GET /solicitacoes/{id}/arquivo)

@pytest.mark.parametrize(
    "conteudo, extensao, tipo",
    [(PDF, ".pdf", "application/pdf"), (PNG, ".png", "image/png"), (JPG, ".jpg", "image/jpeg")],
)
def test_aluno_dono_abre_o_comprovante_com_o_tipo_do_conteudo(client, novo_aluno, enviar, conteudo, extensao, tipo):
    cabecalho = novo_aluno()
    # O nome e o tipo enviados não importam: vale o que o arquivo é
    id_solicitacao = enviar(cabecalho, arquivo=("foto.txt", conteudo, "text/plain")).json()["id"]

    resposta = client.get(f"/solicitacoes/{id_solicitacao}/arquivo", headers=cabecalho)

    assert resposta.status_code == 200
    assert resposta.content == conteudo
    assert resposta.headers["content-type"] == tipo
    assert resposta.headers["content-disposition"] == f'inline; filename="comprovante-{id_solicitacao}{extensao}"'


@pytest.mark.parametrize("cabecalho", ["cabecalho_professor", "cabecalho_coordenador"])
def test_professor_e_coordenador_abrem_o_comprovante(request, client, novo_aluno, enviar, cabecalho):
    id_solicitacao = enviar(novo_aluno()).json()["id"]

    resposta = client.get(f"/solicitacoes/{id_solicitacao}/arquivo", headers=request.getfixturevalue(cabecalho))

    assert resposta.status_code == 200
    assert resposta.content == PDF


def test_outro_aluno_nao_abre_o_comprovante(client, novo_aluno, enviar):
    id_solicitacao = enviar(novo_aluno()).json()["id"]

    resposta = client.get(f"/solicitacoes/{id_solicitacao}/arquivo", headers=novo_aluno())

    assert resposta.status_code == 403
    assert resposta.json()["detail"] == "Acesso negado: o comprovante é de outro aluno"


def test_admin_nao_abre_o_comprovante(client, cabecalho_admin, novo_aluno, enviar):
    id_solicitacao = enviar(novo_aluno()).json()["id"]

    resposta = client.get(f"/solicitacoes/{id_solicitacao}/arquivo", headers=cabecalho_admin)

    assert resposta.status_code == 403
    assert resposta.json()["detail"] == "Acesso negado: recurso restrito ao aluno dono, ao professor e ao coordenador"


def test_comprovante_de_solicitacao_que_nao_existe_devolve_404(client, cabecalho_professor):
    resposta = client.get("/solicitacoes/999999/arquivo", headers=cabecalho_professor)

    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Solicitação não encontrada"


def test_comprovante_apagado_da_pasta_devolve_404(client, novo_aluno, enviar, pasta):
    cabecalho = novo_aluno()
    id_solicitacao = enviar(cabecalho).json()["id"]
    for arquivo in pasta.iterdir():
        arquivo.unlink()

    resposta = client.get(f"/solicitacoes/{id_solicitacao}/arquivo", headers=cabecalho)

    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Comprovante não encontrado"


def test_comprovante_sem_token_devolve_401(client):
    assert client.get("/solicitacoes/1/arquivo").status_code == 401

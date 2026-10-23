import os
import uuid
from pathlib import Path
from urllib.parse import quote_plus

import pymysql
import pytest
from dotenv import dotenv_values
from pymysql.constants import CLIENT

PASTA_BACKEND = Path(__file__).resolve().parents[1]
PASTA_RAIZ = PASTA_BACKEND.parent
BANCO_TESTE = "academic_test"

HOST = os.getenv("TEST_DB_HOST", "127.0.0.1")
PORTA = int(os.getenv("TEST_DB_PORT", "3307"))
SENHA_ROOT = (
    os.getenv("MYSQL_ROOT_PASSWORD")
    or dotenv_values(PASTA_RAIZ / ".env").get("MYSQL_ROOT_PASSWORD")
    or "root_dev"
)

# A API dos testes usa só o banco academic_test, nunca o academic do dia a dia
os.environ["DATABASE_URL"] = f"mysql+pymysql://root:{quote_plus(SENHA_ROOT)}@{HOST}:{PORTA}/{BANCO_TESTE}"
os.environ.setdefault("SECRET_KEY", "chave-usada-somente-nos-testes-automatizados")


def executar_arquivo_sql(cursor, caminho: Path):
    """Roda um arquivo .sql inteiro, com vários comandos, e consome todos os resultados."""
    cursor.execute(caminho.read_text(encoding="utf-8"))
    while cursor.nextset():
        pass


@pytest.fixture(scope="session", autouse=True)
def banco_de_teste():
    """Recria o academic_test do zero com o schema.sql e o seed_base.sql antes dos testes."""
    try:
        conexao = pymysql.connect(
            host=HOST,
            port=PORTA,
            user="root",
            password=SENHA_ROOT,
            charset="utf8mb4",
            client_flag=CLIENT.MULTI_STATEMENTS,
            autocommit=True,
        )
    except pymysql.err.OperationalError as erro:
        pytest.exit(f"Não consegui conectar no MySQL em {HOST}:{PORTA}. Ele está rodando? (docker compose up -d mysql)\n{erro}", returncode=1)

    with conexao:
        with conexao.cursor() as cursor:
            cursor.execute(f"DROP DATABASE IF EXISTS {BANCO_TESTE}")
            cursor.execute(f"CREATE DATABASE {BANCO_TESTE} CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci")
            cursor.execute(f"USE {BANCO_TESTE}")
            executar_arquivo_sql(cursor, PASTA_BACKEND / "database" / "schema.sql")
            executar_arquivo_sql(cursor, PASTA_BACKEND / "database" / "seed_base.sql")
    yield


@pytest.fixture(scope="session")
def client(banco_de_teste):
    from fastapi.testclient import TestClient
    from app.main import app

    return TestClient(app)


@pytest.fixture(scope="session")
def entrar(client):
    """Faz login e devolve o cabeçalho Authorization pronto para usar."""
    def _entrar(email, senha="123456"):
        resposta = client.post("/login", json={"email": email, "senha": senha})
        assert resposta.status_code == 200, resposta.text
        return {"Authorization": f"Bearer {resposta.json()['token']}"}
    return _entrar


@pytest.fixture(scope="session")
def cabecalho_admin(entrar):
    return entrar("admin@teste.com", "admin123")


@pytest.fixture(scope="session")
def cabecalho_coordenador(entrar):
    return entrar("coordenador@teste.com")


@pytest.fixture(scope="session")
def cabecalho_professor(entrar):
    return entrar("professor@teste.com")


@pytest.fixture(scope="session")
def cabecalho_aluno(entrar):
    return entrar("aluno@teste.com")


@pytest.fixture
def dados_aluno():
    """Dados de um aluno novo, com e-mail e matrícula que não se repetem entre os testes."""
    def _dados(**extra):
        sufixo = uuid.uuid4().hex[:8]
        dados = {
            "nome": f"Aluno {sufixo}",
            "email": f"aluno{sufixo}@teste.local",
            "senha": "123456",
            "matricula": f"RA{sufixo}",
            "id_ppc": 1,
        }
        dados.update(extra)
        return dados
    return _dados


@pytest.fixture
def dados_servidor():
    """Dados de um servidor novo (Professor, se não disser outro perfil)."""
    def _dados(**extra):
        sufixo = uuid.uuid4().hex[:8]
        dados = {
            "nome": f"Servidor {sufixo}",
            "email": f"servidor{sufixo}@teste.local",
            "senha": "123456",
            "matricula": f"S{sufixo}",
            "id_perfil": 2,
        }
        dados.update(extra)
        return dados
    return _dados


@pytest.fixture
def novo_servidor(client, cabecalho_admin, dados_servidor):
    """Cadastra um servidor pelo admin e devolve o usuário criado, com a senha usada."""
    def _criar(**extra):
        dados = dados_servidor(**extra)
        resposta = client.post("/usuarios", json=dados, headers=cabecalho_admin)
        assert resposta.status_code == 201, resposta.text
        return {**resposta.json(), "senha": dados["senha"]}
    return _criar


@pytest.fixture
def ppc_valido():
    """Um PPC mínimo que a API aceita: uma categoria, uma subcategoria e uma regra."""
    def _ppc():
        return {
            "id_curso": 1,
            "nome": f"PPC de teste {uuid.uuid4().hex[:8]}",
            "ano": 2026,
            "descricao": "PPC criado pelos testes automatizados",
            "total_pontos": 100,
            "categorias": [
                {
                    "nome": "Atividades de teste",
                    "limite_total": 100,
                    "limite_semestre": 50,
                    "subcategorias": [
                        {
                            "codigo": "1.1",
                            "nome": "Participação em eventos",
                            "documentacao_pedida": "Certificado de participação",
                            "limite_semestre": 30,
                            "regras": [
                                {"titulo_exibicao": "1 ponto por hora", "tipo": "hora", "multiplicador": 1, "operacao": "MULTIPLICACAO"}
                            ],
                        }
                    ],
                }
            ],
        }
    return _ppc

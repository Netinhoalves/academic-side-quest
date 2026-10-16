# Academic Side Quest

Sistema web para alunos enviarem horas complementares e professores validarem. Projeto da disciplina Atividades de Extensão IV, do curso de Tecnologia em Análise e Desenvolvimento de Sistemas (TADS) do IFMS – Campus Três Lagoas.

## Como rodar

Passo a passo para quem acabou de clonar o repositório.

### Pré-requisitos

| Ferramenta | Versão | Para quê |
|---|---|---|
| Docker Desktop | versão atual | Banco de dados MySQL |
| Python | 3.12 ou superior | Backend (API) |
| Node.js | 22 LTS ou superior | Frontend |

### 1. Subir o banco de dados

Na raiz do projeto, crie o arquivo `.env` a partir do exemplo e suba o MySQL.

Git Bash:

```bash
cp .env.example .env
docker compose up -d
docker compose ps
```

CMD (Windows):

```bat
copy .env.example .env
docker compose up -d
docker compose ps
```

Confira as configurações do `.env` antes de subir. Esse arquivo pode conter credenciais e não deve ser versionado no Git.

O MySQL fica disponível na porta **3307** da máquina local. Na primeira vez, o Docker cria o banco `academic` e executa `backend/database/schema.sql` e `backend/database/seed_base.sql`.

### 2. Rodar o backend

Entre na pasta `backend` e crie o ambiente virtual.

Git Bash:

```bash
cd backend
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env
```

CMD (Windows):

```bat
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Gere uma `SECRET_KEY` (a API não inicia sem ela):

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copie o valor gerado para a linha `SECRET_KEY=` do arquivo `backend/.env`. As demais variáveis do exemplo já estão alinhadas com o `compose.yml`.

Com o ambiente virtual ativo, ainda dentro de `backend/`, inicie a API (o comando é o mesmo no Git Bash e no CMD):

```bash
uvicorn app.main:app --reload
```

Abra a documentação interativa em <http://localhost:8000/docs>.

### 3. Rodar o frontend

Em outro terminal, na raiz do projeto (o comando é o mesmo no Git Bash e no CMD):

```bash
cd frontend
npm install
npm run dev
```

O Vite mostra no terminal o endereço da aplicação (por padrão, <http://localhost:5173>).

## Usuários de teste

| Perfil | E-mail | Senha |
|---|---|---|
| Administrador | admin@teste.com | admin123 |
| Coordenador | coordenador@teste.com | 123456 |
| Professor | professor@teste.com | 123456 |
| Aluno | aluno@teste.com | 123456 |

## Problemas comuns

| Sintoma | Solução |
|---|---|
| `SECRET_KEY não definida. Configure-a no arquivo backend/.env` | Rode o `uvicorn` de dentro da pasta `backend/` e confira se o `backend/.env` existe e tem a `SECRET_KEY` preenchida. |
| `ModuleNotFoundError: No module named 'app'` | O `uvicorn` foi executado fora da pasta `backend/`. Entre em `backend/` e rode o comando de novo. |
| Tabelas novas não aparecem no banco | Os scripts de inicialização só são executados quando o volume do banco é criado pela primeira vez. Alterações no schema exigem um procedimento de atualização ou recriação planejada do banco. |
| Container MySQL fica em `Restarting` | Falta o `.env` na raiz do projeto. Crie-o com `cp .env.example .env` (ou `copy .env.example .env` no CMD) e rode `docker compose up -d` de novo. |

## Banco de dados

O projeto utiliza MySQL 8.0 via Docker Compose no ambiente de desenvolvimento.

### Parar o banco de dados

Para parar e remover os containers do projeto:

```bash
docker compose down
```

Esse comando não remove o volume do banco, então os dados continuam na próxima vez que o banco subir.

Para recriar o banco do zero, incluindo schema e seed, remova também o volume:

```bash
docker compose down -v
docker compose up -d
```

**Atenção:** `docker compose down -v` apaga todos os dados armazenados no volume do banco. Use somente se puder perder esses dados.

### Schema do banco de dados

O arquivo `backend/database/schema.sql` define a estrutura atual do banco.

### Estrutura atual

O schema contém as seguintes tabelas:

* Perfil
* Usuario
* Curso
* PPC
* Categoria
* Subcategoria
* RegraPontuacao
* Aluno
* Solicitacao


### Criar e testar um banco separado

Para validar o schema sem afetar os dados do projeto, utilize um banco de testes separado. Nos exemplos abaixo, o nome utilizado é `academic_schema_test`.

Crie um banco exclusivo para testar o schema. O nome `academic_schema_test` abaixo é apenas um exemplo; cada integrante pode escolher outro nome. O comando de criação não apaga um banco que já existe.

```bash
docker compose exec -T mysql sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS academic_schema_test CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;"'
```

Aplique o schema:

```bash
docker compose exec -T mysql sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" academic_schema_test' < backend/database/schema.sql
```

Aplique os dados iniciais:

```bash
docker compose exec -T mysql sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" academic_schema_test' < backend/database/seed_base.sql
```

Se o comando não der erros, confira as tabelas:

```bash
docker compose exec -T mysql sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -D academic_schema_test -e "SHOW TABLES;"'
```

Confira a estrutura do PPC:

```bash
docker compose exec -T mysql sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -D academic_schema_test -e "SHOW CREATE TABLE PPC\G"'
```

Confira as chaves estrangeiras:

```bash
docker compose exec -T mysql sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -D academic_schema_test -e "SELECT COUNT(*) AS total_chaves_estrangeiras FROM information_schema.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA = DATABASE() AND REFERENCED_TABLE_NAME IS NOT NULL;"'
```

Confira os perfis padrão:

```bash
docker compose exec -T mysql sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -D academic_schema_test -e "SELECT id, nome_perfil FROM Perfil ORDER BY id;"'
```

O resultado esperado para o schema atual é de 9 tabelas, 11 chaves estrangeiras e 4 perfis padrão.

### Atualização do schema

O comando `CREATE TABLE IF NOT EXISTS` cria tabelas ausentes, *mas não modifica automaticamente as tabelas que já existem*. Além disso, o Docker só executa o `schema.sql` e o `seed_base.sql` quando o volume do banco é criado.

Se houver alterações estruturais em `backend/database/schema.sql`, o procedimento recomendado é:

1. Testar primeiro em um banco separado e vazio, usando o nome escolhido para o banco de testes.
2. No ambiente de desenvolvimento, aplique as alterações do schema por um procedimento de migração do banco. Se for necessário recriar o banco, faça backup dos dados antes, pois a remoção do volume apaga os dados persistidos.
3. Em um banco que contenha dados reais (por exemplo, o banco hospedado), não recriar: avaliar uma migração SQL apropriada.

O banco de testes é destinado à validação da criação e da estrutura do schema. Cada integrante pode escolher seu próprio nome para ele.

### Regras gerais da modelagem

Cada PPC informa seu próprio `total_pontos`.

As categorias e subcategorias possuem limites de pontuação próprios.

A pontuação calculada e a pontuação efetivamente aproveitada são armazenadas separadamente em Solicitacao.

O backend é responsável por calcular ano e semestre com base em `data_atividade`.

As solicitações possuem os estados PENDENTE, APROVADA e REJEITADA.

O schema define restrições de integridade, chaves estrangeiras e perfis padrão.

### Desenvolvimento em equipe

Antes de iniciar uma alteração no banco:

1. Atualize sua branch com as alterações compartilhadas pela equipe.
2. Confira o estado do Git antes de modificar arquivos.
3. Faça alterações no schema em uma branch de trabalho.
4. Teste o schema em um banco separado.
5. Revise o `git diff` e execute `git diff --check`.
6. Atualize esta documentação quando os procedimentos ou a estrutura mudarem.
7. Envie as alterações para revisão por meio de um Pull Request, seguindo o fluxo de trabalho do grupo.

## Sobre o projeto

O aluno envia os certificados das atividades complementares, o professor ou o coordenador valida o envio, e o sistema calcula os pontos conforme as regras do PPC do curso (1 ponto = 1 hora). O curso TADS exige 275 pontos, distribuídos em quatro categorias, cada uma com limite no curso e por semestre.

### Perfis

| Perfil | O que faz |
|---|---|
| Aluno | Cadastra-se sozinho, envia horas complementares com o certificado e acompanha seu progresso. |
| Professor | Cadastrado pelo coordenador. Valida as horas enviadas pelos alunos. |
| Coordenador | Cadastrado pelo administrador. Cadastra curso, PPC e professores, e também valida horas. |
| Administrador | Cadastra coordenadores. Não é criado pela API. |

## Tecnologias

| Camada | Tecnologias |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy 2, PyMySQL, PyJWT, bcrypt, python-dotenv, Uvicorn |
| Banco de dados | MySQL 8.0, Docker Compose |
| Frontend | React 19, Vite, Tailwind CSS 3 |

## Estrutura do repositório

```text
academic-side-quest/
├── backend/
│   ├── app/                 # API FastAPI (rotas, modelos, schemas, autenticação)
│   ├── database/
│   │   ├── schema.sql       # estrutura do banco
│   │   └── seed_base.sql    # dados iniciais de teste
│   ├── .env.example         # variáveis do backend
│   └── requirements.txt
├── frontend/                # React + Vite + Tailwind
│   ├── public/
│   └── src/
├── .env.example             # variáveis do MySQL (usadas pelo compose.yml)
├── compose.yml              # MySQL 8.0 via Docker
├── LICENSE
└── README.md
```

## Equipe

| Nome | Área |
|---|---|
| Dirceu Neto | Backend |
| Gabriel Oliveira | Backend |
| João Lucas Miranda | Banco de dados |
| Maysson Alexandre de Oliveira | Frontend |
| Victor Cazuo | Frontend |

Professora: Maraísa Guerra, disciplina Atividades de Extensão IV.

## Fluxo de trabalho

| Branch | Uso |
|---|---|
| `main` | Só recebe merge na véspera de cada entrega. |
| `dev-backend` | Integração do backend. |
| `dev-frontend` | Integração do frontend. |
| `feature/TASK-xx-descricao` | Uma branch por tarefa, criada a partir da `dev-backend` ou da `dev-frontend`. |

1. Crie a branch da tarefa a partir da `dev-backend` ou da `dev-frontend`, no padrão `feature/TASK-xx-descricao`.
2. Faça commits pequenos, focados na tarefa, no padrão `TASK-xx tipo: descrição`. Tipos: `feat`, `fix`, `chore`, `docs`, `refactor` e `test`.
3. Abra um Pull Request para a branch de integração e peça revisão. Cada PR precisa de 1 aprovação antes do merge.

## Licença

Distribuído sob a licença MIT. Veja o arquivo [LICENSE](LICENSE).

---

IFMS – Campus Três Lagoas · 2026

# Academic Side Quest

Sistema web para alunos enviarem horas complementares e professores validarem. Projeto da disciplina Atividades de Extensão IV, do curso de Tecnologia em Análise e Desenvolvimento de Sistemas (TADS) do IFMS – Campus Três Lagoas.

## Como rodar

Passo a passo para quem acabou de clonar o repositório. O caminho recomendado inicia **MySQL e API** com Docker Compose; o frontend é iniciado separadamente.

### Pré-requisitos

| Ferramenta | Para quê |
|---|---|
| Docker Desktop ou Docker Engine com Docker Compose | Banco de dados MySQL e API |
| Node.js 22 LTS ou superior | Frontend |
| Python 3.12 ou superior | Necessário somente para executar o backend manualmente |

### 1. Configurar o ambiente e iniciar MySQL + API

Na raiz do projeto, crie o arquivo `.env` a partir do exemplo.

Git Bash, Linux ou macOS:

```bash
cp .env.example .env
```

CMD (Windows):

```bat
copy .env.example .env
```

Gere uma chave secreta para a API:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Se o comando `python` não estiver disponível, tente `python3`. Copie o valor gerado para `SECRET_KEY=` no arquivo `.env` da **raiz do projeto**. Não compartilhe esse valor nem versione o arquivo `.env`.

Com o `.env` configurado, na raiz do projeto execute:

```bash
docker compose up -d --build
docker compose ps
```

O primeiro comando constrói a imagem da API e inicia a API e o MySQL em segundo plano. O segundo mostra o estado dos serviços. Aguarde o MySQL aparecer como `healthy`.

- API: <http://localhost:8000/>
- Documentação interativa da API: <http://localhost:8000/docs>
- MySQL: porta `3307` da máquina local.

Na primeira inicialização de um volume vazio, o MySQL cria o banco `academic` e executa `backend/database/schema.sql` e `backend/database/seed_base.sql`.

### 2. Rodar o frontend

Em outro terminal, na raiz do projeto:

```bash
cd frontend
npm install
npm run dev
```

O Vite mostra no terminal o endereço da aplicação (por padrão, <http://localhost:5173>).

### 3. Executar o backend manualmente (opcional)

Use esta alternativa somente se quiser executar a API fora do container. Se o serviço `api` do Compose já estiver usando a porta `8000`, pare apenas esse serviço antes de iniciar o backend manualmente:

```bash
docker compose stop api
```

Na raiz do projeto, inicie o MySQL pelo Compose:

```bash
docker compose up -d mysql
```

Depois, entre na pasta `backend` e crie o ambiente virtual.

Git Bash, Linux ou macOS:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Windows CMD:

```bat
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Gere uma chave secreta com o comando indicado na etapa 1 e substitua o marcador `SECRET_KEY=` em `backend/.env`. Em execução manual, esse arquivo também precisa conter a `DATABASE_URL` apontando para `localhost:3307`.

Com o ambiente virtual ativo e ainda dentro de `backend/`, inicie a API:

```bash
uvicorn app.main:app --reload
```

A documentação interativa fica em <http://localhost:8000/docs>.

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
| `SECRET_KEY` ausente ou vazia | No fluxo Docker, confira se `SECRET_KEY` está preenchida no `.env` da raiz. Na execução manual, confira `backend/.env`. Não compartilhe a chave nem versione esses arquivos. |
| `ModuleNotFoundError: No module named 'app'` | Na execução manual, entre em `backend/`, ative o ambiente virtual e rode o comando `uvicorn` novamente. |
| Tabelas novas não aparecem no banco | Os scripts de inicialização só são executados quando o volume do banco é criado pela primeira vez. Alterações no schema exigem um procedimento de atualização ou recriação planejada do banco. |
| API não inicia ou reinicia | Confira os logs com `docker compose logs api`. Verifique se o `.env` da raiz existe e contém `SECRET_KEY` preenchida. |

## Banco de dados

O projeto utiliza MySQL 8.0 e a API FastAPI via Docker Compose no ambiente de desenvolvimento.

### Parar os serviços

Para parar e remover os containers da API e do MySQL:

```bash
docker compose down
```

Esse comando remove os containers da API e do MySQL, mas não remove o volume do banco; os dados continuam disponíveis quando os serviços forem iniciados novamente.

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
│   ├── .env.example         # variáveis para execução manual do backend
│   ├── Dockerfile            # imagem da API
│   └── requirements.txt
├── frontend/                # React + Vite + Tailwind
│   ├── public/
│   └── src/
├── .env.example             # variáveis do MySQL (usadas pelo compose.yml)
├── compose.yml              # MySQL 8.0 + API via Docker Compose
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

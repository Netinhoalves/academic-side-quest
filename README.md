# academic-side-quest

Sistema web para gerenciamento, submissão e validação de horas complementares acadêmicas. Projeto da disciplina de Extensão do IFMS.

## Banco de dados — MySQL com Docker

O projeto utiliza MySQL 8.0 via Docker.

### Requisitos

- Docker
- Docker Compose

### Configuração inicial

Copie o arquivo de exemplo:

```bash
cp .env.example .env
```

Confira as configurações do `.env`. Esse arquivo pode conter credenciais e não deve ser enviado ao Git.

### Iniciar o banco

Na raiz do projeto, execute:

```bash
docker compose up -d
docker compose ps
```

O MySQL fica disponível na porta `3307` da máquina local.

### Parar o banco

Para parar e remover os containers sem apagar os dados:

```bash
docker compose down
```

**Atenção:** `docker compose down -v` remove os volumes e pode apagar todos os dados locais do banco. Use somente quando necessário e após fazer backup dos dados importantes.

## Estrutura do banco

Os arquivos em `backend/database/` definem a estrutura e os dados iniciais:

- `schema.sql`: cria as tabelas e relacionamentos.
- `seed_base.sql`: insere perfis e dados básicos para desenvolvimento e testes.

A inicialização automática desses arquivos ocorre somente quando o MySQL utiliza um volume de dados vazio.

O schema atual contém 9 tabelas:

- `Perfil`
- `Usuario`
- `Curso`
- `PPC`
- `Categoria`
- `Subcategoria`
- `RegraPontuacao`
- `Aluno`
- `Solicitacao`

A tabela `PeriodoPPC` não faz parte do schema atual.

## Testes e atualizações

- Teste alterações do schema em um banco separado, sem afetar os dados do projeto.
- Para bancos existentes, alterações estruturais podem exigir uma migração SQL.
- Após mudanças estruturais integradas pela equipe, recrie o ambiente local somente se necessário e conforme combinado com o grupo.

Para recriar o banco a partir dos arquivos de inicialização, após confirmar que pode apagar os dados locais:

```bash
docker compose down -v
docker compose up -d
```

Esse procedimento apaga os volumes do projeto e inicializa o banco novamente. Não o execute se precisar preservar os dados locais.

## Regras da modelagem

- Cada PPC informa seu próprio `total_pontos`.
- Categorias e subcategorias possuem limites de pontuação.
- A pontuação calculada e a pontuação aproveitada são armazenadas separadamente em `Solicitacao`.
- O backend calcula ano e semestre com base em `data_atividade`.
- As solicitações podem ter os estados `PENDENTE`, `APROVADA` e `REJEITADA`.

## Desenvolvimento em equipe

Antes de enviar alterações:

1. Atualize sua branch.
2. Confira o estado do Git.
3. Faça as alterações em uma branch de trabalho.
4. Teste o schema em um banco separado.
5. Revise com `git diff` e execute `git diff --check`.
6. Atualize esta documentação quando necessário.
7. Envie as alterações por Pull Request para revisão.

# academic-side-quest
Sistema web para gerenciamento, submissão e validação de horas complementares acadêmicas. Projeto da disciplina de Extensão do IFMS.

## Banco de dados - MySQL com Docker

O projeto utiliza MySQL 8.0 via Docker para o ambiente de desenvolvimento.

### Requisitos

- Docker
- Docker Compose

### Configuração inicial

Copie o arquivo de exemplo:
	cp .env.example .env

Confira as configurações do arquivo .env antes de iniciar o ambiente.

IMPORTANTE: O arquivo .env pode conter credenciais e não deve ser versionado no Git.

### Subir o banco de dados

Na raiz do projeto, execute:

	docker compose up -d

Confira se o serviço está em execução:

    docker compose ps

O serviço MySQL utiliza a porta 3307 da máquina local, conforme a configuração do Docker Compose.

### Parar o banco de dados

Para parar e remover os containers do projeto:

	docker compose down

Esse comando não remove os volumes persistentes do banco de dados.

Não utilize docker compose down -V sem necessidade, porque -v pode remover os volumes e apagar os dados persistidos do MySQL.

### Schema do Banco de Dados

O arquivo backend/database/schema.sql define a estrutura atual do banco e insere os perfis padrão.

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

A tabela PeriodoPPC não faz parte da estrutual atual.

### Criar e testar um banco separado

Para validar o schema sem afetar os dados do projeto, utilize o banco academic_schema_test.

* Atenção: o prodecimento abaixo apaga e recria somente academic_schema_test. Antes de executá-lo, confirme que não existem dados importantes nele.

Crie o banco de testes:

# docker compose exec -T mysql sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -e "DROP DATABASE IF EXISTS academic_schema_test;" CREATE DATABASE academic_schema_test CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;"'

Aplique o schema:

# docker compose exec -T mysql sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" academic_schema_test' < backend/database/schema.sql

Se o comando não der erros, confira as tabelas:

# docker compose exec -T mysql sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -D academic_schema_test -e "SHOW TABLES;"'

Confira a estrutura do PPC:

# docker compose exec -T mysql sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -D academic_schema_test -e "SHOW CREATE TABLE PPC\G"'

Confira as chaves estrangeiras:

# docker compose exec -T mysql sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -D academic_schema_test -e "SELECT COUNT(*) AS total_chaves_estrangeiras FROM information_schema.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA = DATABASE() AND REFERENCED_TABLE_NAME IS NOT NULL;"'

Configura os perfis padrão:

# docker compose exec -T mysql sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -D academic_schema_test -e "SELECT id, nome_perfil FROM Perfil ORDER BY id;"'

O resultado esperado para o schema atual é de 9 tabelas, 11 chaves estrangeiras e 4 perfis padrão.

### Atualização do schema

O comando CREATE TABLE IF NOT EXISTS cria tabelas ausentes, *mas não modifica automaticamente as tabelas que já existem*.

Se tiver alterações estruturais no backend/database/schema.sql, o procedimento recomendado é testar primeiro em um banco separado e vazio. Para atualizar um banco existente que já contém dados, avalie as alterações necessárias para uma migração SQL apropriada. Não apague nem recrie o banco principal para aplicar alterações de estrutura.

* O banco academic_schema_test é destinado a testes de criação e validação.
* O banco academic deve ser preservado quando contiver dados do projeto.

### Regras gerais da modelagem

Cada PPC informa seu próprio total_pontos.

As categorias e subcategorias possuem limites de pontuação próprios.

A pontuação calculada e a pontuação efetivamente aproveitada são armazenadas separadamente em Solicitacao.

O backend é responsável por calcular ano e semestre com base em data_atividade.

As solicitações possuem os estados PENDENTE, APROVADA e REJEITADA.

O schema define restrições de integridade, chaves estrangeiras e perfis padrão.

### Desenvolvimento em equipe

Antes de iniciar uma alteração no banco:

1. Atualize sua branch com as alterações compartilhadas pela equipe.

2. Confira o estado do Git antes de modificar arquivos.

3. Faça alterações no schema em uma branch de trabalho.

4. Teste o schema em um banco separado.

5. Revise o git diff e execute git diff --check.

6. Atualize esta documentação quando os procedimentos ou a estrutura mudarem.

7. Envie as alterações para revisão por meio de um Pull Request, seguindo o fluxo de trabalho do grupo.

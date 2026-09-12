# academic-side-quest
Sistema web para gerenciamento, submissão e validação de horas complementares acadêmicas. Projeto da disciplina de Extensão do IFMS.

## Banco de dados - Docker

O projeto utiliza MySQL 8.0 via Docker para o ambiente de desenvolvimento.

### Requisitos

- Docker
- Docker Compose

### Configuração

Copie o arquivo de exemplo:
	cp .env.example .env

O arquivo .env já será criado com as configurações necessárias para o ambiente de desenvolvimento.

O arquivo .env não deve ser versionado no Git, pois pode conter credenciais.

### Subir o banco de dados

Execute:

	docker compose up -d

O MySQL será iniciado em um container Docker e ficará disponível na porta 3307 da máquina local.

### Parar o banco de dados

Para parar o container:

	docker compose down

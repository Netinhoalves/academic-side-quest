# Contrato da API da entrega final

Rotas que o back entrega para as telas da entrega final (28/11): envio de atividades pelo aluno, validação pelo professor e pelo coordenador, progresso do aluno e lista de alunos.

O front pode começar agora usando os exemplos deste documento como dados de exemplo: as respostas reais vão ter o mesmo formato. Mudança no contrato só depois de avisar no grupo.

As regras do cálculo dos pontos, com os cenários de teste, estão em [`docs/testes/testes-regras-pontos.md`](../testes/testes-regras-pontos.md).

## 1. Convenções

- **Endereço:** o mesmo `VITE_API_URL` de hoje: `http://localhost:8000` no computador e `/api` no servidor.
- **Login:** toda rota pede o cabeçalho `Authorization: Bearer <token>`, como na etapa 1.
- **Datas:** `AAAA-MM-DD` (`2026-06-10`). Data e hora: `AAAA-MM-DDTHH:MM:SS` (`2026-11-03T10:15:00`).
- **Pontos:** número no JSON (`15`, `7.5`), nunca texto.
- **Semestre:** sai da `data_atividade`: janeiro a junho é o semestre `1`, julho a dezembro é o `2`.
- **Pontos calculados:** nas regras `SOMA`, o `multiplicador` da regra; nas regras `MULTIPLICACAO`, `multiplicador × quantidade`.
- **Pontos aproveitados:** só existem nas solicitações `APROVADA`; nas `PENDENTE` e `REJEITADA` vêm `null`. Valem o menor entre os pontos calculados e os saldos da subcategoria no semestre, da categoria no semestre, da categoria no curso e do PPC, contando as aprovadas pela `data_atividade`, da mais antiga para a mais recente (no empate, a enviada primeiro).
- **Erros:** `{"detail": "mensagem"}`. No `422`, o `detail` pode vir como lista (`[{"msg": "..."}]`); o `api.js` já junta as mensagens.
- **Administrador:** não usa nenhuma destas rotas e recebe `403`.

## 2. Resumo das rotas

| Método | Rota | Quem pode | Para quê |
| --- | --- | --- | --- |
| GET | `/me` | Todos (já existe) | Dados do usuário; para o aluno, o curso e o PPC |
| GET | `/ppcs/{id}` | Todos (já existe) | Categorias, subcategorias e regras do PPC, para a tabela de atividades |
| POST | `/solicitacoes` | Aluno | Enviar uma atividade com o comprovante |
| GET | `/alunos/me/solicitacoes` | Aluno | As solicitações do próprio aluno |
| GET | `/alunos/me/progresso` | Aluno | O progresso do próprio aluno |
| GET | `/solicitacoes` | Professor e Coordenador | Lista para validação |
| PATCH | `/solicitacoes/{id}/aprovar` | Professor e Coordenador | Aprovar |
| PATCH | `/solicitacoes/{id}/rejeitar` | Professor e Coordenador | Recusar, com observação |
| GET | `/alunos` | Professor e Coordenador | Lista de alunos com o progresso |
| GET | `/alunos/{id}` | Professor e Coordenador | Detalhe de um aluno |
| GET | `/solicitacoes/{id}/arquivo` | O aluno dono, Professor e Coordenador | O comprovante |

## 3. Objetos

### 3.1 Solicitação

É o mesmo objeto em todas as rotas que devolvem solicitações. Já vem com os nomes da regra, da subcategoria e da categoria, para o front não precisar cruzar com o PPC. O caminho do arquivo no servidor não sai na resposta: o comprovante é baixado pela rota `/solicitacoes/{id}/arquivo`.

```json
{
  "id": 21,
  "aluno": { "id": 1, "nome": "Aluno Teste", "matricula": "2023000001" },
  "descricao_atividade": "Curso online de Python",
  "data_atividade": "2026-06-10",
  "ano": 2026,
  "semestre": 1,
  "quantidade": 15,
  "pontos_calculados": 15,
  "pontos_aproveitados": 15,
  "status": "APROVADA",
  "observacao": null,
  "regra": { "id": 3, "titulo_exibicao": "1 ponto por hora", "tipo": "hora", "multiplicador": 1, "operacao": "MULTIPLICACAO" },
  "subcategoria": { "id": 3, "codigo": "1.3", "nome": "Realização de cursos de língua estrangeira, informática e outros de formação cultural, social ou específica do âmbito do curso" },
  "categoria": { "id": 1, "nome": "Atividades de aperfeiçoamento e enriquecimento cultural e esportivo" },
  "avaliador": { "id": 3, "nome": "Professor Teste" },
  "created_at": "2026-11-02T09:12:00",
  "updated_at": "2026-11-02T15:40:00"
}
```

| Campo | Observação |
| --- | --- |
| `aluno.id` | O id da tabela Aluno (não o do usuário) |
| `quantidade` | Horas, meses ou outra unidade da regra (`regra.tipo`); `null` nas regras `SOMA` |
| `pontos_aproveitados` | `null` enquanto `PENDENTE` e quando `REJEITADA` |
| `status` | `PENDENTE`, `APROVADA` ou `REJEITADA` |
| `observacao` | Escrita por quem avaliou; obrigatória na recusa |
| `avaliador` | `null` enquanto `PENDENTE` |
| `created_at` | Data do envio |
| `updated_at` | Data da última mudança; depois da avaliação, é a data da avaliação |

As outras três solicitações do mesmo aluno, usadas nos exemplos das rotas:

```json
[
  {
    "id": 22,
    "aluno": { "id": 1, "nome": "Aluno Teste", "matricula": "2023000001" },
    "descricao_atividade": "Monitoria de Algoritmos",
    "data_atividade": "2026-08-18",
    "ano": 2026,
    "semestre": 2,
    "quantidade": null,
    "pontos_calculados": 15,
    "pontos_aproveitados": 15,
    "status": "APROVADA",
    "observacao": null,
    "regra": { "id": 5, "titulo_exibicao": "15 pontos por participação", "tipo": "participação", "multiplicador": 15, "operacao": "SOMA" },
    "subcategoria": { "id": 5, "codigo": "2.1", "nome": "Monitoria remunerada ou voluntária" },
    "categoria": { "id": 2, "nome": "Atividades de divulgação científica e de iniciação à docência" },
    "avaliador": { "id": 3, "nome": "Professor Teste" },
    "created_at": "2026-11-02T09:20:00",
    "updated_at": "2026-11-02T15:41:00"
  },
  {
    "id": 23,
    "aluno": { "id": 1, "nome": "Aluno Teste", "matricula": "2023000001" },
    "descricao_atividade": "Participação no grupo de pesquisa em inteligência artificial",
    "data_atividade": "2026-09-01",
    "ano": 2026,
    "semestre": 2,
    "quantidade": 4,
    "pontos_calculados": 30,
    "pontos_aproveitados": null,
    "status": "PENDENTE",
    "observacao": null,
    "regra": { "id": 18, "titulo_exibicao": "7,5 pontos por mês", "tipo": "mês", "multiplicador": 7.5, "operacao": "MULTIPLICACAO" },
    "subcategoria": { "id": 14, "codigo": "4.1", "nome": "Participação em projetos e grupos de pesquisa" },
    "categoria": { "id": 4, "nome": "Atividades de pesquisa ou extensão e publicações" },
    "avaliador": null,
    "created_at": "2026-11-03T10:15:00",
    "updated_at": "2026-11-03T10:15:00"
  },
  {
    "id": 24,
    "aluno": { "id": 1, "nome": "Aluno Teste", "matricula": "2023000001" },
    "descricao_atividade": "Ouvinte em banca de TCC",
    "data_atividade": "2026-10-07",
    "ano": 2026,
    "semestre": 2,
    "quantidade": null,
    "pontos_calculados": 3,
    "pontos_aproveitados": null,
    "status": "REJEITADA",
    "observacao": "O certificado não tem o nome do aluno.",
    "regra": { "id": 12, "titulo_exibicao": "3 pontos por participação", "tipo": "participação", "multiplicador": 3, "operacao": "SOMA" },
    "subcategoria": { "id": 10, "codigo": "3.3", "nome": "Participação como ouvinte em eventos acadêmicos, tais como bancas de TCC, dissertação, teses" },
    "categoria": { "id": 3, "nome": "Atividades de vivência acadêmica e profissional complementar" },
    "avaliador": { "id": 3, "nome": "Professor Teste" },
    "created_at": "2026-11-03T10:30:00",
    "updated_at": "2026-11-03T16:05:00"
  }
]
```

### 3.2 Progresso

Traz todas as categorias e subcategorias do PPC do aluno, mesmo as que ainda não têm pontos, com os limites ao lado. Só contam as solicitações `APROVADA`.

- `total_exigido`: o `total_pontos` do PPC.
- `percentual`: `total_aproveitado / total_exigido × 100`, com 2 casas, de 0 a 100.
- `pendentes`: quantas solicitações do aluno estão `PENDENTE`.
- `semestres`: só os semestres em que a categoria ou a subcategoria teve pontos; sem pontos, a lista vem vazia.

No exemplo abaixo aparecem só algumas subcategorias, para encurtar. Na resposta real vêm todas.

```json
{
  "total_exigido": 275,
  "total_aproveitado": 30,
  "percentual": 10.91,
  "pendentes": 1,
  "categorias": [
    {
      "id": 1,
      "nome": "Atividades de aperfeiçoamento e enriquecimento cultural e esportivo",
      "limite_total": 120,
      "limite_semestre": 80,
      "aproveitado_total": 15,
      "semestres": [{ "ano": 2026, "semestre": 1, "aproveitado": 15 }],
      "subcategorias": [
        { "id": 1, "codigo": "1.1", "nome": "Participação como agente em atividades culturais: filme, teatro, apresentações artísticas, feiras, exposições, festivais e competições esportivas, bandas, coral, olimpíadas em geral", "limite_semestre": 30, "aproveitado_total": 0, "semestres": [] },
        { "id": 3, "codigo": "1.3", "nome": "Realização de cursos de língua estrangeira, informática e outros de formação cultural, social ou específica do âmbito do curso", "limite_semestre": 40, "aproveitado_total": 15, "semestres": [{ "ano": 2026, "semestre": 1, "aproveitado": 15 }] }
      ]
    },
    {
      "id": 2,
      "nome": "Atividades de divulgação científica e de iniciação à docência",
      "limite_total": 100,
      "limite_semestre": 60,
      "aproveitado_total": 15,
      "semestres": [{ "ano": 2026, "semestre": 2, "aproveitado": 15 }],
      "subcategorias": [
        { "id": 5, "codigo": "2.1", "nome": "Monitoria remunerada ou voluntária", "limite_semestre": 60, "aproveitado_total": 15, "semestres": [{ "ano": 2026, "semestre": 2, "aproveitado": 15 }] }
      ]
    },
    {
      "id": 3,
      "nome": "Atividades de vivência acadêmica e profissional complementar",
      "limite_total": 100,
      "limite_semestre": 60,
      "aproveitado_total": 0,
      "semestres": [],
      "subcategorias": [
        { "id": 10, "codigo": "3.3", "nome": "Participação como ouvinte em eventos acadêmicos, tais como bancas de TCC, dissertação, teses", "limite_semestre": 18, "aproveitado_total": 0, "semestres": [] }
      ]
    },
    {
      "id": 4,
      "nome": "Atividades de pesquisa ou extensão e publicações",
      "limite_total": 100,
      "limite_semestre": 80,
      "aproveitado_total": 0,
      "semestres": [],
      "subcategorias": [
        { "id": 14, "codigo": "4.1", "nome": "Participação em projetos e grupos de pesquisa", "limite_semestre": 45, "aproveitado_total": 0, "semestres": [] }
      ]
    }
  ]
}
```

### 3.3 Aluno

Usado na lista de alunos e no detalhe.

```json
{
  "id": 1,
  "id_usuario": 4,
  "nome": "Aluno Teste",
  "email": "aluno@teste.com",
  "matricula": "2023000001",
  "data_ingresso": "2023-02-01",
  "curso": { "id": 1, "nome": "Tecnologia em Análise e Desenvolvimento de Sistemas", "sigla": "TADS", "instituicao": "IFMS - Campus Três Lagoas", "ativo": true },
  "ppc": { "id": 1, "nome": "PPC TADS 2019", "ano": 2019 },
  "total_exigido": 275,
  "total_aproveitado": 30,
  "percentual": 10.91,
  "pendentes": 1
}
```

## 4. Rotas do aluno

### 4.1 POST `/solicitacoes`

Envia uma atividade com o comprovante. O corpo é `multipart/form-data` (formulário com arquivo), não JSON.

| Campo | Tipo | Regras |
| --- | --- | --- |
| `id_regra_pontuacao` | número | Uma regra do PPC do próprio aluno |
| `descricao_atividade` | texto | De 3 a 500 caracteres |
| `data_atividade` | data `AAAA-MM-DD` | Não pode ser futura nem ter mais de 6 meses (documento de lógica) |
| `quantidade` | número | Obrigatória e maior que zero nas regras `MULTIPLICACAO` (horas ou meses); nas regras `SOMA` não é usada e, se vier, a API ignora |
| `arquivo` | arquivo | PDF, JPG ou PNG, até 5 MB |

No front, monte com `FormData` e não defina o `Content-Type`: o navegador monta o multipart sozinho.

```js
const dados = new FormData();
dados.append('id_regra_pontuacao', 3);
dados.append('descricao_atividade', 'Curso online de Python');
dados.append('data_atividade', '2026-06-10');
dados.append('quantidade', 15);
dados.append('arquivo', arquivo); // o File do <input type="file">
await fetch(`${API_BASE_URL}/solicitacoes`, { method: 'POST', headers: { Authorization: `Bearer ${token}` }, body: dados });
```

**Resposta `201`:** o objeto Solicitação criado, com `status` `PENDENTE`, `pontos_calculados` preenchido e `pontos_aproveitados` `null`.

| Código | Quando | Mensagem |
| --- | --- | --- |
| `400` | A regra não existe ou é de outro PPC | `A regra não pertence ao PPC do aluno` |
| `403` | Quem enviou não é aluno | `Acesso negado: recurso restrito a usuários com perfil Aluno` |
| `413` | Arquivo maior que 5 MB | `O arquivo deve ter no máximo 5 MB` |
| `422` | Arquivo que não é PDF, JPG ou PNG | `O arquivo deve ser PDF, JPG ou PNG` |
| `422` | Data futura | `A data da atividade não pode ser futura` |
| `422` | Data com mais de 6 meses | `A atividade deve ter sido realizada nos últimos 6 meses` |
| `422` | Regra `MULTIPLICACAO` sem quantidade | `Informe a quantidade` |
| `422` | Outro campo faltando ou inválido | Mensagem do Pydantic |

### 4.2 GET `/alunos/me/solicitacoes`

As solicitações do aluno logado, da `data_atividade` mais recente para a mais antiga.

- Filtro opcional: `?status=PENDENTE` (ou `APROVADA`, `REJEITADA`).
- **Resposta `200`:** lista de Solicitação. No exemplo, a lista traz as solicitações 24, 23, 22 e 21, nessa ordem.
- `403` se quem chamou não é aluno.

### 4.3 GET `/alunos/me/progresso`

**Resposta `200`:** o objeto Progresso do aluno logado (exemplo na seção 3.2). `403` se quem chamou não é aluno.

## 5. Rotas do professor e do coordenador

### 5.1 GET `/solicitacoes`

Lista para validação, da mais antiga para a mais nova (pela data do envio).

| Filtro | Exemplo | Observação |
| --- | --- | --- |
| `status` | `?status=PENDENTE` | Sem filtro, vêm todas |
| `id_ppc` | `?id_ppc=1` | Só alunos desse PPC |
| `id_aluno` | `?id_aluno=1` | Só esse aluno |

**Resposta `200`:** lista de Solicitação. Exemplo de `GET /solicitacoes?status=PENDENTE`: uma lista só com a solicitação 23.

### 5.2 PATCH `/solicitacoes/{id}/aprovar`

Corpo JSON, com a observação opcional (até 1000 caracteres):

```json
{ "observacao": "Declaração conferida." }
```

**Resposta `200`:** a Solicitação atualizada. Aprovando a 23 do exemplo, ela volta com `status` `APROVADA`, `pontos_aproveitados` `30`, `observacao` `Declaração conferida.` e `avaliador` preenchido.

A cada aprovação ou recusa, a API recalcula os pontos aproveitados de todas as aprovadas do aluno, em ordem de `data_atividade`. Depois de avaliar, o front deve buscar a lista de novo, porque outras solicitações do mesmo aluno podem mudar.

| Código | Quando | Mensagem |
| --- | --- | --- |
| `403` | Quem chamou não é professor nem coordenador | `Acesso negado: recurso restrito a usuários com perfil Professor ou Coordenador` |
| `404` | A solicitação não existe | `Solicitação não encontrada` |
| `409` | A solicitação já foi avaliada | `Solicitação já avaliada` |

### 5.3 PATCH `/solicitacoes/{id}/rejeitar`

Corpo JSON, com a observação obrigatória (de 3 a 1000 caracteres), que o aluno vai ver:

```json
{ "observacao": "O certificado não tem o nome do aluno." }
```

**Resposta `200`:** a Solicitação com `status` `REJEITADA`, `pontos_aproveitados` `null` e a observação. Mesmos erros do aprovar, mais `422` sem observação (`Informe o motivo da recusa`).

### 5.4 GET `/alunos`

Alunos com o progresso resumido, em ordem alfabética.

| Filtro | Exemplo | Observação |
| --- | --- | --- |
| `id_ppc` | `?id_ppc=1` | Só alunos desse PPC (usado pelo "Gerenciar alunos" do PPC) |
| `busca` | `?busca=2023` | Parte do nome ou da matrícula, sem diferenciar maiúsculas |

**Resposta `200`:** lista de Aluno (exemplo na seção 3.3).

### 5.5 GET `/alunos/{id}`

O `id` é o da tabela Aluno (`aluno.id`). **Resposta `200`:**

```js
{
  aluno: alunoExemplo,          // o objeto Aluno (seção 3.3)
  progresso: progressoExemplo,  // o objeto Progresso (seção 3.2)
  solicitacoes: [solicitacao24, solicitacao23, solicitacao22, solicitacao21] // como em GET /alunos/me/solicitacoes
}
```

`404` se o aluno não existe.

## 6. Comprovante

### 6.1 GET `/solicitacoes/{id}/arquivo`

Devolve o arquivo em si, com o `Content-Type` dele (`application/pdf`, `image/jpeg` ou `image/png`), para abrir no navegador.

- Pode baixar: o aluno dono da solicitação, professor e coordenador. Outro aluno recebe `403`; solicitação inexistente, `404`.
- Um link direto (`<a href>`) não manda o token. No front, busque com `fetch` e o cabeçalho de login, transforme em `blob` e abra com `URL.createObjectURL`:

```js
const resposta = await fetch(`${API_BASE_URL}/solicitacoes/${id}/arquivo`, { headers: { Authorization: `Bearer ${token}` } });
const url = URL.createObjectURL(await resposta.blob());
window.open(url, '_blank'); // ou use a url num <iframe> (PDF) ou num <img> (imagem)
```

## 7. Se sobrar tempo

- **PATCH `/solicitacoes/{id}/desfazer`:** volta uma solicitação avaliada para `PENDENTE` e recalcula. Permite trocar uma aprovação por recusa, como no cenário 15 dos testes do cálculo.
- **Aviso de recálculo:** a mensagem para o aluno quando um recálculo muda os pontos de uma solicitação (cenário 7 dos testes do cálculo).

## 8. Quem faz cada parte

| Parte | Task |
| --- | --- |
| `POST /solicitacoes`, `GET /alunos/me/solicitacoes` e `GET /solicitacoes/{id}/arquivo` | TASK-55 (Dirceu) |
| Pasta dos comprovantes no Docker e no servidor | TASK-56 (Dirceu) |
| Cálculo dos pontos aproveitados | TASK-57 (Gabriel) |
| `GET /solicitacoes`, aprovar e rejeitar | TASK-58 (Gabriel) |
| `GET /alunos/me/progresso`, `GET /alunos` e `GET /alunos/{id}` | TASK-59 (Dirceu) |
| Telas Comprovar horas e Visualizar resultados | TASK-62 e TASK-63 (Maysson) |
| Telas Validar solicitações e Visualizar alunos | TASK-64 e TASK-65 (Cazuo) |

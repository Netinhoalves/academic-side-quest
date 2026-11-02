# Testes das regras de cálculo de pontos

## 1. Objetivo

Documentar cenários de teste para validar o cálculo nas solicitações de horas complementares do Academic Side Quest.

Esse documento será usado como referência para implementação e validação do cálculo no backend.

## 2. Regras gerais

### 2.1 Pontos calculados

O cálculo depende da operação definida na regra de pontuação:

- `SOMA`: usa o valor fixo definido na regra.
- `MULTIPLICACAO`: multiplica o valor da regra pela quantidade na solicitação.

### 2.2 Pontos aproveitados

Os pontos aproveitados não podem ultrapassar o menor valor disponível entre os limites:

1. Limite da subcategoria no semestre.
2. Limite da categoria no semestre.
3. Limite total da categoria no PPC.
4. Limite total de pontos do PPC.

A quantidade de pontos aproveitados será o menor valor entre os pontos calculados e os saldos disponíveis nos quatro limites.

### 2.3 Período da atividade

O semestre é determinado pela data da atividade (`data_atividade`):

- Janeiro a junho: primeiro semestre.
- Julho a dezembro: segundo semestre.

Os limites semestrais são independentes. O saldo de um semestre não vai para o outro.

### 2.4 Situação da solicitação

- Solicitações aprovadas são consideradas no cálculo.
- Solicitações rejeitadas não somam pontos.
- Solicitações pendentes não são consideradas no cálculo e não consomem pontos.
- A ordem de distribuição dos pontos considera a data da atividade, da mais antiga para a mais recente, independe da ordem em que foram avaliadas.
- **Solicitações com a mesma data de atividade:** devem ser processadas pela ordem de chegada ao sistema. A solicitação recebida primeiro tem prioridade na distribuição dos pontos.
- **Quantidade inválida:** solicitações com quantidade zero, negativa ou ausente não devem ter seus pontos calculados.
- **Precisão dos pontos:** não é necessário aplicar arredondamento, pois os valores decimais previstos nas regras são múltiplos de 7,5.

## 3. Limites do PPC TADS 2019

| Categoria | Limite por semestre | Limite total |
|-------------|---:|----:|
| Categoria 1 | 80 | 120 |
| Categoria 2 | 60 | 100 |
| Categoria 3 | 60 | 100 |
| Categoria 4 | 80 | 100 |
| **Total do PPC** | — | **275** |

## 4. Limites das subcategorias

| Subcategoria | Limite por semestre |
|---|---:|
| 1.1 | 30 |
| 1.2 | 30 |
| 1.3 | 40 |
| 1.4 | 40 |
| 2.1 | 60 |
| 2.2 | 30 |
| 2.3 | 20 |
| 3.1 | 30 |
| 3.2 | 20 |
| 3.3 | 18 |
| 3.4 | 40 |
| 3.5 | 20 |
| 3.6 | 45 |
| 4.1 | 45 |
| 4.2 | 45 |
| 4.3 | 50 |
| 4.4 | 50 |
| 4.5 | 10 |

## 5. Cenários de teste

Os cenários serão documentados com as solicitações envolvidas, as datas das atividades, as regras aplicadas, a situação de cada solicitação e os resultados esperados.


### 5.1 Cenário 1 — Cálculo básico de atividade por hora

**Objetivo:** verificar se o sistema calcula corretamente os pontos de uma atividade com a operação `MULTIPLICACAO`, quando todos os limites têm saldo suficiente.

**Regra utilizada:**

| Informação | Valor |
|-------------------------------------|-------------------------------------------------|
| Categoria                           |                                               1 |
| Subcategoria                        | 1.3 — Cursos de informática, idiomas e formação |
| ID da regra                         |                                               3 |
| Regra de pontuação                  |                                1 ponto por hora |
| Operação                            |                                   MULTIPLICACAO |
| Limite da subcategoria por semestre |                                       40 pontos |
| Limite da categoria por semestre    |                                       80 pontos |
| Limite total da categoria no PPC    |                                      120 pontos |
| Limite total do PPC                 |                                      275 pontos |

**Dados de entrada:**

| Solicitação | Data da atividade | Regra utilizada | Quantidade | Situação |
|---|------------|----------------------------|---------:|----------|
| A | 10/03/2026 | Regra 3 — 1 ponto por hora | 15 horas | Aprovada |

**Cálculo esperado:**

15 horas × 1 ponto = 15 pontos calculados.

**Resultado esperado:**

| Solicitação | Pontos calculados | Saldo da subcategoria antes | Saldo da categoria no semestre antes | Saldo total da categoria antes | Saldo do PPC antes | Pontos aproveitados |
|---|---:|---:|---:|----:|----:|---:|
| A | 15 | 40 | 80 | 120 | 275 | 15 |

**Saldos após o aproveitamento:**

| Limite | Saldo inicial | Pontos utilizados | Saldo restante |
|------------------------------|----:|---:|----:|
| Subcategoria 1.3 no semestre |  40 | 15 |  25 |
| Categoria 1 no semestre      |  80 | 15 |  65 |
| Categoria 1 no PPC           | 120 | 15 | 105 |
| Total do PPC                 | 275 | 15 | 260 |

**Resultado esperado:** os 15 pontos calculados devem ser totalmente aproveitados, já que todos os limites tem saldo suficiente.

**Validações:**
- Aplicação correta da regra 3.
- Cálculo correto da operação `MULTIPLICACAO`.
- Respeito aos quatro limites de aproveitamento.
- Aproveitamento integral dos pontos quando não há restrições.


### 5.2 Cenário 2 — Ultrapassar o limite da subcategoria

**Objetivo:** verificar se o sistema impede que uma subcategoria ultrapasse seu limite semestral, mesmo quando as solicitações geram mais pontos.

**Regra utilizada:**

| Informação | Valor |
|-------------------------------------|-------------------------------------------------|
| Categoria                           |                                               1 |
| Subcategoria                        | 1.3 — Cursos de informática, idiomas e formação |
| ID da regra                         |                                               3 |
| Regra de pontuação                  |                                1 ponto por hora |
| Operação                            |                                   MULTIPLICACAO |
| Limite da subcategoria por semestre |                                       40 pontos |
| Limite da categoria por semestre    |                                       80 pontos |
| Limite total da categoria no PPC    |                                      120 pontos |
| Limite total do PPC                 |                                      275 pontos |

**Dados de entrada:**

| Solicitação | Data da atividade | Regra utilizada | Quantidade | Situação |
|---|------------|----------------------------|---------:|----------|
| A | 10/03/2026 | Regra 3 — 1 ponto por hora | 25 horas | Aprovada |
| B | 20/04/2026 | Regra 3 — 1 ponto por hora | 20 horas | Aprovada |

**Cálculo esperado:**

- Solicitação A: 25 horas × 1 ponto = 25 pontos calculados.
- Solicitação B: 20 horas × 1 ponto = 20 pontos calculados.

**Resultado esperado:**

| Solicitação | Pontos calculados | Saldo da subcategoria antes | Saldo da categoria no semestre antes | Saldo total da categoria antes | Saldo do PPC antes | Pontos aproveitados |
|---|---:|---:|---:|----:|----:|---:|
| A | 25 | 40 | 80 | 120 | 275 | 25 |
| B | 20 | 15 | 55 |  95 | 250 | 15 |

**Saldos após o aproveitamento:**

| Limite | Saldo inicial | Pontos utilizados | Saldo restante |
|------------------------------|----:|---:|----:|
| Subcategoria 1.3 no semestre |  40 | 40 |   0 |
| Categoria 1 no semestre      |  80 | 40 |  40 |
| Categoria 1 no PPC           | 120 | 40 |  80 |
| Total do PPC                 | 275 | 40 | 235 |

**Justificativa:** a solicitação A utiliza 25 dos 40 pontos disponíveis na subcategoria. Restam 15 pontos para a solicitação B. Embora B gere 20 pontos, somente 15 podem ser aproveitados, pois o limite semestral da subcategoria foi atingido.

**Validações:**
- Aplicação correta da regra 3.
- Identificação do saldo restante da subcategoria após cada solicitação.
- Bloqueio dos 5 pontos que ultrapassariam o limite.
- Os limites da categoria e do PPC não devem restringir o aproveitamento neste cenário.


### 5.3. Cenário 3 — Limite da categoria no semestre

**Objetivo:** verificar se o limite semestral da categoria é aplicado corretamente quando várias solicitações de subcategorias diferentes consomem seus pontos.

**Categoria utilizada:** Categoria 1 — Atividades de aperfeiçoamento e enriquecimento cultural e esportivo.

**Limites aplicáveis:**
- Categoria por semestre: 80 pontos.
- Categoria total do curso: 120 pontos.
- Subcategoria 1.1: 30 pontos por semestre.
- Subcategoria 1.2: 30 pontos por semestre.
- Subcategoria 1.3: 40 pontos por semestre.
- Subcategoria 1.4: 40 pontos por semestre.
- PPC: 275 pontos.

**Solicitações:**

Todas as solicitações pertencem ao primeiro semestre de 2026 e estão aprovadas.

| Solicitação | Data da atividade | Subcategoria | Regra | Quantidade | Calculados | Aproveitados |
|---|------------|-----|----------------------------------|---------------:|---:|---:|
| A | 10/03/2026 | 1.3 | Regra 3 — 1 ponto por hora       |    40 horas    | 40 | 40 |
| B | 11/03/2026 | 1.1 | Regra 1 — 5 pontos por atividade | 1 atividade    |  5 |  5 |
| C | 12/03/2026 | 1.1 | Regra 1 — 5 pontos por atividade | 1 atividade    |  5 |  5 |
| D | 13/03/2026 | 1.1 | Regra 1 — 5 pontos por atividade | 1 atividade    |  5 |  5 |
| E | 14/03/2026 | 1.1 | Regra 1 — 5 pontos por atividade | 1 atividade    |  5 |  5 |
| F | 15/03/2026 | 1.1 | Regra 1 — 5 pontos por atividade | 1 atividade    |  5 |  5 |
| G | 16/03/2026 | 1.2 | Regra 2 — 5 pontos por visita    | 1 visita       |  5 |  5 |
| H | 17/03/2026 | 1.2 | Regra 2 — 5 pontos por visita    | 1 visita       |  5 |  5 |
| I | 18/03/2026 | 1.4 | Regra 4 — 10 por participação    | 1 participação | 10 |  5 |

**Saldo dos limites após cada solicitação:**

| Após solicitação | Subcategoria utilizada | Saldo da subcategoria | Saldo da categoria no semestre | Saldo da categoria total | Saldo do PPC |
|---|------------|---:|---:|---:|----:|
| A | 1.3: 40/40 |  0 | 40 | 80 | 235 |
| B | 1.1: 5/30  | 25 | 35 | 75 | 230 |
| C | 1.1: 10/30 | 20 | 30 | 70 | 225 |
| D | 1.1: 15/30 | 15 | 25 | 65 | 220 |
| E | 1.1: 20/30 | 10 | 20 | 60 | 215 |
| F | 1.1: 25/30 |  5 | 15 | 55 | 210 |
| G | 1.2: 5/30  | 25 | 10 | 50 | 205 |
| H | 1.2: 10/30 | 20 |  5 | 45 | 200 |
| I | 1.4: 5/40  | 35 |  0 | 40 | 195 |

**Resultado esperado:**

A solicitação I calcula 10 pontos, mas aproveita somente 5, pois restam apenas 5 pontos no limite semestral da Categoria 1.

A subcategoria 1.4 ainda possui 35 pontos disponíveis após a solicitação, enquanto a categoria ainda possui 40 pontos disponíveis no limite total do curso e o PPC possui 195 pontos disponíveis. Portanto, o único limite que restringe a solicitação I é o limite semestral da categoria.

**Validações do cenário:**
- As solicitações são processadas pela data da atividade.
- Todas as subcategorias respeitam seus limites semestrais.
- O limite semestral da categoria é compartilhado entre suas subcategorias.
- A solicitação I tem seus pontos aproveitados parcialmente devido ao limite da categoria.
- O limite total da categoria e o limite do PPC não interferem no resultado.


### 5.4. Cenário 4 — Limite total da categoria no curso

**Objetivo:** verificar se o limite total da categoria é respeitado considerando os pontos aproveitados em dois semestres.

**Categoria utilizada:** Categoria 1 — Atividades de aperfeiçoamento e enriquecimento cultural e esportivo.

**Limites aplicáveis:**
- Categoria por semestre: 80 pontos.
- Categoria total do curso: 120 pontos.
- Subcategoria 1.3: 40 pontos por semestre.
- Subcategoria 1.4: 40 pontos por semestre.
- PPC: 275 pontos.

**Solicitações do primeiro semestre de 2026:**

Todas as solicitações estão aprovadas.

| Solicitação | Data da atividade | Subcategoria | Regra | Quantidade | Calculados | Aproveitados |
|---|------------|-----|-------------------------------|---------------:|---:|---:|
| A | 10/03/2026 | 1.3 | Regra 3 — 1 ponto por hora    |       40 horas | 40 | 40 |
| B | 11/03/2026 | 1.4 | Regra 4 — 10 por participação | 1 participação | 10 | 10 |
| C | 12/03/2026 | 1.4 | Regra 4 — 10 por participação | 1 participação | 10 | 10 |
| D | 13/03/2026 | 1.4 | Regra 4 — 10 por participação | 1 participação | 10 | 10 |
| E | 14/03/2026 | 1.4 | Regra 4 — 10 por participação | 1 participação | 10 | 10 |

Total aproveitado no primeiro semestre: **80 pontos**.

**Solicitações do segundo semestre de 2026:**

Todas as solicitações estão aprovadas.

| Solicitação | Data da atividade | Subcategoria | Regra | Quantidade | Calculados | Aproveitados |
|---|------------|-----|-------------------------------|---------------:|---:|---:|
| F | 10/08/2026 | 1.3 | Regra 3 — 1 ponto por hora    |       35 horas | 35 | 35 |
| G | 11/08/2026 | 1.4 | Regra 4 — 10 por participação | 1 participação | 10 |  5 |
| H | 12/08/2026 | 1.4 | Regra 4 — 10 por participação | 1 participação | 10 |  0 |

**Conferência dos saldos antes da solicitação G:**

| Limite | Utilizado | Saldo |
|--------------------------------------|----:|----:|
| Subcategoria 1.4 no segundo semestre |   0 |  40 |
| Categoria 1 no segundo semestre      |  35 |  45 |
| Categoria 1 no total do curso        | 115 |   5 |
| PPC                                  | 115 | 160 |

**Resultado esperado:**

A solicitação G gera 10 pontos, mas aproveita 5, porque tem só 5 pontos no limite total da Categoria 1.

Depois da solicitação G:
- Categoria 1 no segundo semestre: 40 pontos utilizados, com saldo de 40.
- Categoria 1 no total do curso: 120 pontos utilizados, com saldo de 0.
- Subcategoria 1.4 no segundo semestre: 5 pontos utilizados, com saldo de 35.
- PPC: 120 pontos utilizados, com saldo de 155.

A solicitação H tem 10 pontos, mas aproveita 0, já que o limite total da categoria foi atingido.

**Resultado final:**
- Categoria 1 no primeiro semestre: 80/80 pontos.
- Categoria 1 no segundo semestre: 40/80 pontos.
- Categoria 1 no total do curso: 120/120 pontos.
- PPC: 120/275 pontos.

**Validações do cenário:**
- Os limites das subcategorias são respeitados em cada semestre.
- O limite semestral da categoria é reiniciado no segundo semestre.
- O limite total da categoria acumula os pontos dos dois semestres.
- A solicitação G é aproveitada parcialmente devido ao limite total da categoria.
- A solicitação H não aproveita pontos porque o limite total da categoria já foi atingido.
- O limite do PPC não interfere no resultado.


### 5.5. Cenário 5 — Limite total do PPC

**Objetivo:** verificar se o sistema impede que o aluno ultrapasse o limite total de 275 pontos do PPC, mesmo quando ainda tem pontos disponíveis nos limites das categorias e subcategorias.

**PPC utilizado:** TADS 2019 — limite total de 275 pontos.

**Solicitações do primeiro semestre de 2026:**

Todas as solicitações estão aprovadas e devem ser processadas em ordem cronológica pela data da atividade.

| Solicitação | Data da atividade | Subcategoria | Regra | Quantidade | Calculados | Aproveitados |
|---|------------|-----|-------------------------------|---------------:|---:|---:|
| A | 10/03/2026 | 1.3 | Regra 3 — 1 ponto por hora    |       40 horas | 40 | 40 |
| B | 11/03/2026 | 1.4 | Regra 4 — 10 por participação | 1 participação | 10 | 10 |
| C | 12/03/2026 | 1.4 | Regra 4 — 10 por participação | 1 participação | 10 | 10 |
| D | 13/03/2026 | 1.4 | Regra 4 — 10 por participação | 1 participação | 10 | 10 |
| E | 14/03/2026 | 1.4 | Regra 4 — 10 por participação | 1 participação | 10 | 10 |
| F | 15/03/2026 | 2.1 | Regra 5 — 15 por participação | 1 participação | 15 | 15 |
| G | 16/03/2026 | 2.1 | Regra 5 — 15 por participação | 1 participação | 15 | 15 |
| H | 17/03/2026 | 2.1 | Regra 5 — 15 por participação | 1 participação | 15 | 15 |
| I | 18/03/2026 | 2.1 | Regra 5 — 15 por participação | 1 participação | 15 | 15 |
| J | 19/03/2026 | 3.1 | Regra 9 — 1 ponto por hora    |       30 horas | 30 | 30 |
| K | 20/03/2026 | 3.4 | Regra 13 — 1 ponto por hora   |       30 horas | 30 | 30 |
| L | 21/03/2026 | 4.1 | Regra 18 — 7,5 pontos por mês |        4 meses | 30 | 30 |
| M | 22/03/2026 | 4.3 | Regra 20 — 25 por publicação  |   1 publicação | 25 | 25 |
| N | 23/03/2026 | 4.4 | Regra 22 — 15 por publicação  |   1 publicação | 15 | 15 |
| O | 24/03/2026 | 4.5 | Regra 24 — 5 por publicação   |   1 publicação |  5 |  5 |
| P | 25/03/2026 | 4.5 | Regra 24 — 5 por publicação   |   1 publicação |  5 |  0 |

**Saldos disponíveis para a solicitação P:**

| Categoria        | Pontos aproveitados | Limite aplicável | Saldo |
|------------------|--------------------:|-----------------:|------:|
| Categoria 1      |                  80 |               80 |     0 |
| Categoria 2      |                  60 |               60 |     0 |
| Categoria 3      |                  60 |               60 |     0 |
| Categoria 4      |                  75 |               80 |     5 |
| **Total do PPC** |             **275** |          **275** | **0** |

**Conferência dos limites antes da solicitação P:**
- Subcategoria 4.5: 5 pontos utilizados de 10, com saldo de 5.
- Categoria 4 no semestre: 75 pontos utilizados de 80, com saldo de 5.
- Categoria 4 no total do curso: 75 pontos utilizados de 100, com saldo de 25.
- PPC: 275 pontos utilizados de 275, com saldo de 0.

**Resultado esperado:**

A solicitação P calcula 5 pontos, mas aproveita 0, pois o limite total do PPC já foi atingido.

Mesmo que ainda tenham pontos disponíveis na subcategoria 4.5 e nos limites semestral e total da Categoria 4, o PPC não possui mais saldo.

**Resultado final:**
- Categoria 1: 80 pontos.
- Categoria 2: 60 pontos.
- Categoria 3: 60 pontos.
- Categoria 4: 75 pontos.
- Total do PPC: 275/275 pontos.

**Validações do cenário:**
- As subcategorias respeitam seus limites semestrais.
- As categorias respeitam seus limites semestrais e totais.
- O limite global do PPC considera os pontos aproveitados em todas as categorias.
- A solicitação P não aproveita pontos porque o PPC atingiu seu limite total.
- O bloqueio ocorre exclusivamente pelo limite global do PPC.


### 5.6. Cenário 6 — Solicitações aprovadas, rejeitadas e pendentes

**Objetivo:** verificar se somente as solicitações aprovadas entram no cálculo dos pontos aproveitados.

**Categoria utilizada:** Categoria 1 — Atividades de aperfeiçoamento e enriquecimento cultural e esportivo.

**Subcategoria utilizada:** 1.3 — Cursos de língua estrangeira, informática e formação cultural/social/específica do curso.

**Regra utilizada:** Regra 3 — 1 ponto por hora (MULTIPLICACAO).

**Limites aplicáveis:**
- Subcategoria 1.3: 40 pontos por semestre.
- Categoria 1 por semestre: 80 pontos.
- Categoria 1 no total do curso: 120 pontos.
- PPC: 275 pontos.

**Solicitações:**

Todas são do primeiro semestre de 2026 e devem ser consideradas em ordem cronológica pela data da atividade.

| Solicitação | Data da atividade | Quantidade | Calculados | Status | Aproveitados |
|---|------------|---------:|---:|-----------|---:|
| A | 10/03/2026 | 10 horas | 10 | Aprovada  | 10 |
| B | 11/03/2026 | 15 horas |  — | Rejeitada |  0 |
| C | 12/03/2026 | 20 horas |  — | Pendente  |  0 |
| D | 13/03/2026 |  5 horas |  5 | Aprovada  |  5 |

**Resultado esperado:**

- Solicitação A: calcula e aproveita 10 pontos.
- Solicitação B: não calcula nem aproveita pontos por estar rejeitada.
- Solicitação C: não calcula nem aproveita pontos por estar pendente.
- Solicitação D: calcula e aproveita 5 pontos.

**Saldos finais:**

| Limite | Utilizado | Saldo |
|-------------------------------|---:|----:|
| Subcategoria 1.3              | 15 |  25 |
| Categoria 1 no semestre       | 15 |  65 |
| Categoria 1 no total do curso | 15 | 105 |
| PPC                           | 15 | 260 |

**Validações do cenário:**
- Solicitações aprovadas são contabilizadas.
- Solicitações pendentes e rejeitadas não participam do cálculo nem consomem pontos dos limites disponíveis.


### 5.7. Cenário 7 — Ordem cronológica das atividades

**Objetivo:** verificar se o sistema prioriza as atividades mais antigas, mesmo quando uma atividade mais recente foi aprovada primeiro.

**Categoria utilizada:** Categoria 1.

**Subcategoria utilizada:** 1.3 — Cursos de língua estrangeira, informática e formação cultural/social/específica do curso.

**Regra utilizada:** Regra 3 — 1 ponto por hora (MULTIPLICACAO).

**Limites aplicáveis:**
- Subcategoria 1.3: 40 pontos por semestre.
- Categoria 1 por semestre: 80 pontos.
- Categoria 1 no total do curso: 120 pontos.
- PPC: 275 pontos.

**Solicitações:**

As duas solicitações pertencem ao primeiro semestre de 2026 e estão aprovadas.

| Solicitação | Data da atividade | Quantidade | Calculados | Ordem de aprovação |
|---|------------|---------:|---:|----------------------------|
| A | 10/03/2026 | 30 horas | 30 | Aprovada em segundo lugar  |
| B | 20/03/2026 | 20 horas | 20 | Aprovada em primeiro lugar |

**Resultado esperado após a aprovação das duas solicitações:**

| Solicitação | Pontos calculados | Pontos aproveitados |
|----------------------------|---:|---:|
| A — atividade mais antiga  | 30 | 30 |
| B — atividade mais recente | 20 | 10 |

**Saldos finais:**

| Limite | Utilizado | Saldo |
|-------------------------------|---:|----:|
| Subcategoria 1.3              | 40 |   0 |
| Categoria 1 no semestre       | 40 |  40 |
| Categoria 1 no total do curso | 40 |  80 |
| PPC                           | 40 | 235 |

**Explicação:**

A solicitação B foi aprovada primeiro e poderia receber 20 pontos. Mas quando a solicitação A, mais antiga, for aprovada, o sistema deverá recalcular a distribuição.

A solicitação A tem prioridade e recebe 30 pontos. A solicitação B fica com os 10 pontos restantes do limite da subcategoria.

**Notificação ao usuário:**

Sempre que ocorrer um recálculo que altere os pontos aproveitados de uma solicitação, o sistema deverá apresentar uma mensagem explicando o motivo da alteração.

Exemplo de mensagem:

"Os pontos aproveitados foram recalculados para respeitar a ordem cronológica das atividades. Atividades mais antigas possuem prioridade."


### 5.8. Cenário 8 — Atingir exatamente o limite da subcategoria

**Objetivo:** verificar se o sistema aproveita integralmente os pontos quando uma solicitação atinge exatamente o limite da subcategoria, sem ultrapassar.

**Categoria utilizada:** Categoria 1.

**Subcategoria utilizada:** 1.3 — Cursos de língua estrangeira, informática e formação cultural/social/específica do curso.

**Regra utilizada:** Regra 3 — 1 ponto por hora (MULTIPLICACAO).

**Limites aplicáveis:**
- Subcategoria 1.3: 40 pontos por semestre.
- Categoria 1 por semestre: 80 pontos.
- Categoria 1 no total do curso: 120 pontos.
- PPC: 275 pontos.

**Solicitações:**

Todas pertencem ao primeiro semestre de 2026 e estão aprovadas.

| Solicitação | Data da atividade | Quantidade | Calculados | Aproveitados |
|---|------------|---------:|---:|---:|
| A | 10/03/2026 | 25 horas | 25 | 25 |
| B | 20/03/2026 | 15 horas | 15 | 15 |

**Resultado esperado:**

- Solicitação A: aproveita 25 pontos.
- Solicitação B: aproveita 15 pontos.
- Total aproveitado na subcategoria: 40 pontos.

**Saldos finais:**

| Limite | Utilizado | Saldo |
|-------------------------------|---:|----:|
| Subcategoria 1.3              | 40 |   0 |
| Categoria 1 no semestre       | 40 |  40 |
| Categoria 1 no total do curso | 40 |  80 |
| PPC                           | 40 | 235 |

**Validações do cenário:**
- Os pontos calculados são integralmente aproveitados.
- A subcategoria atinge exatamente seu limite de 40 pontos.
- Nenhum limite é ultrapassado.
- Não ocorre bloqueio nem redução de pontos.
- O sistema apresenta corretamente o saldo zero da subcategoria.


### 5.9. Cenário 9 — Atingir exatamente o limite semestral da categoria

**Objetivo:** verificar se o sistema aproveita integralmente as solicitações até atingir exatamente o limite de 60 pontos da Categoria 2.

**Categoria utilizada:** Categoria 2 — Atividades de divulgação científica e de iniciação à docência.

**Limites aplicáveis:**
- Categoria 2 por semestre: 60 pontos.
- Categoria 2 no total do curso: 100 pontos.
- Subcategoria 2.1: 60 pontos por semestre.
- Subcategoria 2.2: 30 pontos por semestre.
- Subcategoria 2.3: 20 pontos por semestre.
- PPC: 275 pontos.

**Solicitações:**

Todas pertencem ao primeiro semestre de 2026 e estão aprovadas.

| Solicitação | Data da atividade | Subcategoria | Regra | Quantidade | Calculados | Aproveitados |
|---|---|---|---|---:|---:|---:|
| A | 10/03/2026 | 2.1 | Regra 5 — 15 por participação | 1 participação | 15 | 15 |
| B | 11/03/2026 | 2.1 | Regra 5 — 15 por participação | 1 participação | 15 | 15 |
| C | 12/03/2026 | 2.2 | Regra 6 — 10 por participação | 1 participação | 10 | 10 |
| D | 13/03/2026 | 2.2 | Regra 7 — 15 na área do curso | 1 participação | 15 | 15 |
| E | 14/03/2026 | 2.3 | Regra 8 — 05 por participação | 1 participação | 05 | 05 |

**Resultado esperado:**

Todas as solicitações aproveitam os pontos calculados, totalizando exatamente 60 pontos na Categoria 2.

**Saldos finais:**

| Limite | Utilizado | Saldo |
|-------------------------------|---:|----:|
| Subcategoria 2.1              | 30 |  30 |
| Subcategoria 2.2              | 25 |   5 |
| Subcategoria 2.3              |  5 |  15 |
| Categoria 2 no semestre       | 60 |   0 |
| Categoria 2 no total do curso | 60 |  40 |
| PPC                           | 60 | 215 |

**Validações do cenário:**
- Todas as solicitações são integralmente aproveitadas.
- Nenhuma subcategoria ultrapassa seu limite.
- A Categoria 2 atinge exatamente os 60 pontos semestrais.
- O saldo semestral da categoria fica zerado.
- O limite total da categoria e o limite do PPC continuam com saldo disponível.
- Não ocorre bloqueio nem redução de pontos.


### 5.10. Cenário 10 — Atingir exatamente o limite total da categoria

**Objetivo:** verificar se o sistema acumula corretamente os pontos dos dois semestres até atingir o limite total de 100 pontos da Categoria 2.

**Categoria utilizada:** Categoria 2 — Atividades de divulgação científica e de iniciação à docência.

**Limites aplicáveis:**
- Categoria 2 por semestre: 60 pontos.
- Categoria 2 no total do curso: 100 pontos.
- Subcategoria 2.1: 60 pontos por semestre.
- Subcategoria 2.2: 30 pontos por semestre.
- PPC: 275 pontos.

**Solicitações do primeiro semestre de 2026:**

Todas as solicitações estão aprovadas.

| Solicitação | Data da atividade | Subcategoria | Regra | Quantidade | Calculados | Aproveitados |
|---|---|---|---|---:|---:|---:|
| A | 10/03/2026 | 2.1 | Regra 5 — 15 por participação | 1 participação | 15 | 15 |
| B | 11/03/2026 | 2.1 | Regra 5 — 15 por participação | 1 participação | 15 | 15 |
| C | 12/03/2026 | 2.1 | Regra 5 — 15 por participação | 1 participação | 15 | 15 |
| D | 13/03/2026 | 2.1 | Regra 5 — 15 por participação | 1 participação | 15 | 15 |

Total aproveitado no primeiro semestre: **60 pontos**.

**Solicitações do segundo semestre de 2026:**

Todas as solicitações estão aprovadas.

| Solicitação | Data da atividade | Subcategoria | Regra | Quantidade | Calculados | Aproveitados |
|---|---|---|---|---:|---:|---:|
| E | 10/08/2026 | 2.1 | Regra 5 — 15 por participação | 1 participação | 15 | 15 |
| F | 11/08/2026 | 2.1 | Regra 5 — 15 por participação | 1 participação | 15 | 15 |
| G | 12/08/2026 | 2.2 | Regra 6 — 10 por participação | 1 participação | 10 | 10 |

Total aproveitado no segundo semestre: **40 pontos**.

**Conferência dos limites:**

| Limite | Utilizado | Saldo |
|--------------------------------------|----:|----:|
| Subcategoria 2.1 — primeiro semestre | 60  |   0 |
| Subcategoria 2.1 — segundo semestre  | 30  |  30 |
| Subcategoria 2.2 — segundo semestre  | 10  |  20 | 
| Categoria 2 — primeiro semestre      | 60  |   0 |
| Categoria 2 — segundo semestre       | 40  |  20 |
| Categoria 2 — total do curso         | 100 |   0 |
| PPC                                  | 100 | 175 |

**Resultado esperado:**

Todas as solicitações aproveitam integralmente os pontos calculados. A Categoria 2 atinge exatamente 100 pontos no total do curso, sem ultrapassar o limite.

**Validações do cenário:**
- Os pontos dos dois semestres são acumulados no limite total da categoria.
- O limite semestral é independente em cada semestre.
- Os limites das subcategorias são respeitados separadamente em cada semestre.
- A categoria atinge exatamente 100 pontos.
- O saldo total da categoria fica zerado.
- O limite do PPC continua com saldo disponível.
- Não ocorre bloqueio nem redução de pontos.


### 5.11. Cenário 11 — Reinicialização dos limites no segundo semestre

**Objetivo:** verificar se os limites semestrais das subcategorias e categorias são reiniciados no segundo semestre, sem carregar o consumo do primeiro.

**Categoria utilizada:** Categoria 1 — Atividades de aperfeiçoamento e enriquecimento cultural e esportivo.

**Subcategoria utilizada:** 1.3 — Cursos de língua estrangeira, informática e formação cultural/social/específica do curso.

**Regra utilizada:** Regra 3 — 1 ponto por hora (MULTIPLICACAO).

**Limites aplicáveis:**
- Subcategoria 1.3: 40 pontos por semestre.
- Categoria 1 por semestre: 80 pontos.
- Categoria 1 no total do curso: 120 pontos.
- PPC: 275 pontos.

**Solicitações:**

Todas as solicitações estão aprovadas.

| Solicitação | Data da atividade | Semestre | Quantidade | Calculados | Aproveitados |
|---|------------|-------------|---------:|---:|---:|
| A | 30/06/2026 | 1º semestre | 40 horas | 40 | 40 |
| B | 01/07/2026 | 2º semestre | 40 horas | 40 | 40 |

**Resultado esperado:**

- Solicitação A: gera 40 pontos, usando o limite da subcategoria no 1º semestre.
- Solicitação B: usa outros 40 pontos, referente ao 2º semestre e com novo limite.

**Saldos finais:**

| Limite                               | Utilizado | Saldo |
|--------------------------------------|----------:|------:|
| Subcategoria 1.3 — primeiro semestre |        40 |     0 |
| Subcategoria 1.3 — segundo semestre  |        40 |     0 |
| Categoria 1 — primeiro semestre      |        40 |    40 |
| Categoria 1 — segundo semestre       |        40 |    40 |
| Categoria 1 — total do curso         |        80 |    40 |
| PPC                                  |        80 |   195 |

**Validações do cenário:**
- Atividades realizadas até 30 de junho pertencem ao primeiro semestre.
- Atividades realizadas a partir de 1º de julho pertencem ao segundo semestre.
- O limite da subcategoria é reiniciado no segundo semestre.
- O limite semestral da categoria também é reiniciado.
- O limite total da categoria e o limite do PPC continuam acumulando os pontos dos dois semestres.
- Nenhuma solicitação tem seus pontos reduzidos.


### 5.12. Cenário 12 — Diferentes regras de cálculo na Categoria 3

**Objetivo:** validar o cálculo de diferentes regras da Categoria 3, sem atingir os limites de pontuação.

**Limites aplicáveis:**
- Categoria 3: 60 pontos por semestre e 100 pontos no total.
- Limites das subcategorias que usamos de base:
  - 3.1: 30 pontos;
  - 3.2: 20 pontos;
  - 3.3: 18 pontos;
  - 3.4: 40 pontos;
  - 3.5: 20 pontos;
  - 3.6: 45 pontos.
- PPC: 275 pontos.

**Solicitações — primeiro semestre de 2026:**

| Solicitação | Subcategoria | Regra | Quantidade | Calculados | Aproveitados |
|---|-----|----------------------------------------|-----------:|----:|----:|
| A | 3.1 | Regra 10 — 10 pontos por evento sem CH | 1 evento   |  10 |  10 |
| B | 3.2 | Regra 11 — 5 pontos por participação   | 1 presença |   5 |   5 |
| C | 3.3 | Regra 12 — 3 pontos por participação   | 1 presença |   3 |   3 |
| D | 3.4 | Regra 14 — 10 pontos por evento sem CH | 1 evento   |  10 |  10 |
| E | 3.5 | Regra 16 — 8 pontos por evento sem CH  | 1 evento   |   8 |   8 |
| F | 3.5 | Regra 15 — 1 ponto por hora            | 4 horas    |   4 |   4 |
| G | 3.6 | Regra 17 — 7,5 pontos por mês          | 1 mês      | 7,5 | 7,5 |
| H | 3.1 | Regra  9 — 1 ponto por hora            | 5 horas    |   5 |   5 |

Todas as solicitações são aprovadas e processadas em ordem cronológica, conforme suas datas de atividade.

**Resultado esperado:**

- Total calculado: **52,5 pontos**.
- Total aproveitado: **52,5 pontos**.
- Categoria 3 no semestre: 52,5 de 60 pontos utilizados; saldo de 7,5.
- Categoria 3 no curso: 52,5 de 100 pontos utilizados; saldo de 47,5.
- PPC: 52,5 de 275 pontos utilizados; saldo de 222,5.

**Saldo por subcategoria:**

| Subcategoria | Utilizados | Limite | Saldo |
|--------------|-----------:|-------:|------:|
| 3.1          |         10 |     30 |    20 |
| 3.2          |          5 |     20 |    15 |
| 3.3          |          3 |     18 |    15 |
| 3.4          |         10 |     40 |    30 |
| 3.5          |         12 |     20 |     8 |
| 3.6          |        7,5 |     45 |  37,5 |

**O que o cenário valida:**
- Regras 10, 11, 12, 14, 15, 16 e 17 da Categoria 3.
- Operações `SOMA` e `MULTIPLICACAO` para calcular as horas.
- Regras de evento sem carga horária.
- Cálculo por quantidade de horas e meses.
- Precisão no cálculo de valores decimais.
- Acúmulo de pontos entre diferentes subcategorias da mesma categoria.


### 5.13. Cenário 13 — Regras de publicação e limites da Categoria 4

**Objetivo:** validar as regras de pontuação por mês e publicação, diferenciando publicações normais das em revista ou periódico da área do curso.

**Limites aplicáveis:**
- Categoria 4: 80 pontos por semestre e 100 pontos no total do curso.
- Subcategoria 4.2: 45 pontos por semestre.
- Subcategoria 4.3: 50 pontos por semestre.
- Subcategoria 4.4: 50 pontos por semestre.
- PPC: 275 pontos.

**Solicitações — primeiro semestre de 2026:**

| Solicitação | Data da atividade | Subcategoria | Regra | Quantidade | Calculados | Aproveitados |
|---|------------|-----|----------------------------------|---------:|----:|----:|
| A | 10/03/2026 | 4.2 | Regra 19 — 7,5 pontos por mês    |    1 mês | 7,5 | 7,5 |
| B | 11/03/2026 | 4.3 | Regra 20 — 25 publicação normal  | 1 publi. |  25 |  25 |
| C | 12/03/2026 | 4.3 | Regra 21 — 30 publicação na área | 1 publi. |  30 |  25 |
| D | 13/03/2026 | 4.4 | Regra 22 — 15 publicação normal  | 1 publi. |  15 |  15 |
| E | 14/03/2026 | 4.4 | Regra 23 — 20 publicação na área | 1 publi. |  20 | 7,5 |

Todas as solicitações são aprovadas e processadas em ordem, seguindo suas datas de atividade.

**Resultado esperado:**

- Total calculado: **97,5 pontos**.
- Total aproveitado: **80 pontos**.
- A solicitação C recebe apenas 25 dos 30 pontos calculados porque a subcategoria 4.3 atinge seu limite de 50 pontos.
- A solicitação E recebe apenas 7,5 dos 20 pontos calculados porque a Categoria 4 atinge seu limite semestral de 80 pontos.

**Saldo por subcategoria:**

| Subcategoria | Utilizados | Limite | Saldo |
|--------------|-----------:|-------:|------:|
| 4.2          |        7,5 |     45 |  37,5 |
| 4.3          |         50 |     50 |     0 |
| 4.4          |       22,5 |     50 |  27,5 |

**Saldo dos limites gerais:**

| Limite                  | Utilizados | Limite | Saldo |
|-------------------------|-----------:|-------:|------:|
| Categoria 4 no semestre |         80 |     80 |     0 |
| Categoria 4 no curso    |         80 |    100 |    20 |
| PPC                     |         80 |    275 |   195 |

**O que o cenário valida:**
- Regras 19, 20, 21, 22 e 23.
- Diferenciação entre publicações normais e na área específica do curso.
- Cálculo decimal com multiplicação por mês.
- Aplicação do limite da subcategoria 4.3.
- Aplicação do limite semestral da Categoria 4.
- Processamento das solicitações em ordem cronológica.


### 5.14. Cenário 14 — Soma de pontuação por múltiplas atividades

**Objetivo:** verificar se o sistema soma corretamente a pontuação fixa de cada atividade ou participação realizada pelo aluno.

**Limites aplicáveis:**
- Categoria 1: 80 pontos por semestre e 120 no total do curso.
- Subcategoria 1.1: 30 pontos por semestre.
- Subcategoria 1.4: 40 pontos por semestre.
- PPC: 275 pontos.

**Solicitações — primeiro semestre de 2026:**

| Solicitação | Data da atividade | Subcategoria | Regra | Quantidade | Pontos calculados | Pontos Aproveitados |
|---|------------|-----|-------------------------------|--------:|---:|---:|
| A | 10/03/2026 | 1.1 | Regra 1 — 5 por atividade     | 1 atvs. |  5 |  5 |
| B | 10/03/2026 | 1.1 | Regra 1 — 5 por atividade     | 1 atvs. |  5 |  5 |
| C | 10/03/2026 | 1.1 | Regra 1 — 5 por atividade     | 1 atvs. |  5 |  5 |
| D | 10/03/2026 | 1.4 | Regra 4 — 10 por participação | 1 part. | 10 | 10 |
| E | 10/03/2026 | 1.4 | Regra 4 — 10 por participação | 1 part. | 10 | 10 |

As cinco solicitações são aprovadas. Todas pertencem ao primeiro semestre de 2026.

**Resultado esperado:**

- Solicitações 1.1: 3 atividades, cada uma vale 5 pontos. Total calculado: 15 pontos.
- Solicitações 1.4: 2 participações, cada uma vale 10 pontos. Total calculado: 20 pontos.
- Total calculado: **35 pontos**.
- Total aproveitado: **35 pontos**.

**Saldo dos limites:**

| Limite                  | Utilizados | Limite | Saldo |
|-------------------------|-----------:|-------:|------:|
| Subcategoria 1.1        |         15 |     30 |    15 |
| Subcategoria 1.4        |         20 |     40 |    20 |
| Categoria 1 no semestre |         35 |     80 |    45 |
| Categoria 1 no curso    |         35 |    120 |    85 |
| PPC                     |         35 |    275 |   240 |

**O que o cenário valida:**
- Operação `SOMA`.
- Cada atividade ou participação possui uma pontuação fixa definida pela regra.
- A pontuação é acumulada conforme a quantidade de ocorrências realizadas.
- Comportamento da operação `SOMA`, sem multiplicar os pontos pela quantidade informada.
- Aplicação dos limites de subcategoria, categoria e PPC.


### 5.15. Cenário 15 — Reavaliação dos limites após alteração de aprovação

**Objetivo:** verificar se o sistema recalcula corretamente pontos aproveitados quando uma solicitação aprovada é rejeitada e quando uma solicitação pendente é aprovada.

**Limites aplicáveis:**
- Categoria 1: 80 pontos por semestre e 120 no total do curso.
- Subcategoria 1.3: 40 pontos por semestre.
- PPC: 275 pontos.

**Solicitações — primeiro semestre de 2026:**

| Solicitação | Data | Quantidade | Estado inicial | Após 1ª alteração | Após 2ª alteração |
|---|------------|---------:|----------|----------:|----------:|
| A | 10/03/2026 | 25 horas | Aprovada | Rejeitada | Rejeitada |
| B | 20/03/2026 | 20 horas | Aprovada |  Aprovada |  Aprovada |
| C | 25/03/2026 | 10 horas | Pendente |  Pendente |  Aprovada |

**Resultado esperado — situação inicial:**

- Solicitação A: 25 pontos aproveitados.
- Solicitação B: 15 pontos aproveitados, devido ao limite restante da subcategoria 1.3.
- Solicitação C: não calcula nem aproveita pontos, pois está pendente.
- Total aproveitado: **40 pontos**.
- Saldo da subcategoria 1.3: 0 pontos.

**Primeira alteração — solicitação A passa de aprovada para rejeitada:**

O sistema deverá desconsiderar os pontos da solicitação A e recalcular os pontos das demais solicitações aprovadas.

| Solicitação | Situação após alteração | Pontos calculados | Pontos aproveitados |
|-------------|-------------------------|------------------:|--------------------:|
| A           | Rejeitada               |                 — |                   0 |
| B           | Aprovada                |                20 |                  20 |
| C           | Pendente                |                 — |                   0 |

**Resultado esperado após a primeira alteração:**

- Total aproveitado: **20 pontos**.
- Subcategoria 1.3: 20 de 40 pontos utilizados; saldo de 20.
- Categoria 1 no semestre: 20 de 80 pontos utilizados; saldo de 60.
- Categoria 1 no curso: 20 de 120 pontos utilizados; saldo de 100.
- PPC: 20 de 275 pontos utilizados; saldo de 255.

**Segunda alteração — solicitação C passa de pendente para aprovada:**

O sistema deverá calcular os pontos da solicitação C e atualizar os pontos aproveitados, respeitando a ordem cronológica das atividades.

| Solicitação |    Status | Pontos calculados | Pontos aproveitados |
|-------------|-----------|------------------:|--------------------:|
| A           | Rejeitada |                 — |                   0 |
| B           |  Aprovada |                20 |                  20 |
| C           |  Aprovada |                10 |                  10 |

**Resultado esperado após a segunda alteração:**

- Solicitação A: 0 pontos aproveitados, pois está rejeitada.
- Solicitação B: 20 pontos aproveitados.
- Solicitação C: 10 pontos aproveitados.
- Total aproveitado: **30 pontos**.
- Subcategoria 1.3: 30 de 40 pontos utilizados; saldo de 10.
- Categoria 1 no semestre: 30 de 80 pontos utilizados; saldo de 50.
- Categoria 1 no curso: 30 de 120 pontos utilizados; saldo de 90.
- PPC: 30 de 275 pontos utilizados; saldo de 245.

**O que o cenário valida:**

- Rejeição de uma solicitação anteriormente aprovada.
- Aprovação de uma solicitação anteriormente pendente.
- Solicitações rejeitadas e pendentes não participam do cálculo nem consomem limites.
- Solicitações aprovadas passam a participar do cálculo.
- Recálculo automático dos pontos aproveitados após mudanças de status.
- Redistribuição dos pontos conforme a ordem cronológica das atividades.
- Atualização dos saldos dos limites após a alteração.


## 6. Catálogo das regras de pontuação

As regras abaixo correspondem às 24 regras cadastradas no PPC TADS 2019, seguindo o arquivo `backend/database/seed_base.sql`.

O limite informado representa a quantidade máxima de pontos aproveitáveis naquela subcategoria durante cada semestre.

| ID da regra | Subcategoria | Regra de pontuação | Tipo de quantidade | Valor | Operação | Limite semestral |
|---:|-----|-------------------------------|--------------------|----:|------|---:|
|  1 | 1.1 |        5 pontos por atividade |          atividade |   5 | SOMA | 30 |
|  2 | 1.2 |           5 pontos por visita |             visita |   5 | SOMA | 30 |
|  3 | 1.3 |              1 ponto por hora |               hora |   1 | MULT.| 40 |
|  4 | 1.4 |   10 por participação provada |       participação |  10 | SOMA | 40 |
|  5 | 2.1 |           15 por participação |       participação |  15 | SOMA | 60 |
|  6 | 2.2 |           10 por participação |       participação |  10 | SOMA | 30 |
|  7 | 2.2 |   15 por participação na área |      part. na área |  15 | SOMA | 30 |
|  8 | 2.3 |            5 por participação |       participação |   5 | SOMA | 20 |
|  9 | 3.1 |              1 ponto por hora |               hora |   1 | MULT.| 30 |
| 10 | 3.1 |          10 por evento sem CH |             evento |  10 | SOMA | 30 |
| 11 | 3.2 |            5 por participação |       participação |   5 | SOMA | 20 |
| 12 | 3.3 |            3 por participação |       participação |   3 | SOMA | 18 |
| 13 | 3.4 |              1 ponto por hora |               hora |   1 | MULT.| 40 |
| 14 | 3.4 |          10 por evento sem CH |             evento |  10 | SOMA | 40 |
| 15 | 3.5 |              1 ponto por hora |               hora |   1 | MULT.| 20 |
| 16 | 3.5 |    8 pontos por evento sem CH |             evento |   8 | SOMA | 20 |
| 17 | 3.6 |            7,5 pontos por mês |                mês | 7,5 | MULT.| 45 |
| 18 | 4.1 |            7,5 pontos por mês |                mês | 7,5 | MULT.| 45 |
| 19 | 4.2 |            7,5 pontos por mês |                mês | 7,5 | MULT.| 45 |
| 20 | 4.3 |             25 por publicação |         publicação |  25 | SOMA | 50 |
| 21 | 4.3 |  30 por publicação em revista | publicação na área |  30 | SOMA | 50 |
| 22 | 4.4 |             15 por publicação |         publicação |  15 | SOMA | 50 |
| 23 | 4.4 |  20 por publicação em revista | publicação na área |  20 | SOMA | 50 |
| 24 | 4.5 |              5 por publicação |         publicação |   5 | SOMA | 10 |

### 6.1 Interpretação das operações

- `SOMA`: o valor definido na regra é atribuído por ocorrência. A quantidade não multiplica esse valor.
- `MULTIPLICACAO`: o valor definido na regra é multiplicado pela quantidade informada na solicitação.

Exemplos:

- Regra 1: uma atividade gera 5 pontos.
- Regra 3: uma atividade de 15 horas gera 15 pontos.
- Regra 17: uma atividade de 2 meses gera 15 pontos.


# Resumo do Trabalho — Pipeline OMA (solver + metaheurística)

Documento que registra **tudo o que foi feito** no código e o **racional** de cada decisão.
Serve como histórico de mudanças e guia rápido. Referências de código no formato `arquivo:linha`.

Documentos relacionados: [`specification.md`](specification.md),
[`parameters.md`](parameters.md), [`test_division.md`](test_division.md),
[`test_plan.md`](test_plan.md).

---

## 0. Estado inicial (o que estava quebrado)

O ponto de entrada `src/oma/main.py` **não rodava** — quebrava em toda invocação:

- `getSolverType()` era chamado mas **nunca definido/importado** → `NameError` imediato.
- A variável `number` era usada onde o nome correto era `instance_number` → `NameError` após o
  solve.
- Código morto e inalcançável depois de um `return`, referenciando funções inexistentes
  (`load()`, `Logger`, `instance.affinity`).

Além disso, a **metaheurística** (greedy + tabu) também estava quebrada: lia `instance.a` (a lista
de triplas `(i, j, afinidade)`) e a indexava como matriz 2D → `IndexError: tuple index out of
range`.

A **formulação do modelo** (`solvers/model.py`) estava correta e foi mantida.

---

## 1. Correção do runner + reconciliação de conflitos

**O que:** corrigidos os bugs de `NameError`, removido o código morto, e resolvidos marcadores de
conflito de merge deixados em `main.py` e `solvers/generic.py`.

**Por quê:** sem isso nada executava. Na resolução de conflito do `generic.py`, mantivemos a versão
**parametrizada** `GenericSolver.create(solver_type, time_limit=...)` em vez de um limite fixo
embutido — mais flexível e testável.

**Resultado:** o pipeline passou a carregar e rodar.

---

## 2. Três modos de execução

**O que:** o `main.py` passou a expor três formas de teste, conforme pedido:

1. **Solver para todas as instâncias** — `uv run oma --cplex all` (ou `--highs all`).
2. **Metaheurística para todas as instâncias** — `uv run oma --tabu all`.
3. **Solver e depois metaheurística** — `uv run oma --cplex --tabu all` (roda **todas** as
   instâncias no solver primeiro, depois **todas** na metaheurística).

Aceita também uma instância única no lugar de `all` (ex.: `--cplex 3`).

**Por quê:** o trabalho exige comparar o método exato com a metaheurística sobre o mesmo conjunto
de instâncias; ter os três modos num único CLI evita scripts paralelos e mantém a saída
consistente.

**Racional do ordenamento (modo 3):** "todas no solver, depois todas na metaheurística" (e não
intercalado por instância) foi uma escolha explícita do usuário, refletida no laço de `main()`.

---

## 3. Correção da metaheurística — `Instance.affinity`

**O que:** adicionada uma propriedade `affinity` (matriz n×n simétrica, com cache) à dataclass
`Instance` (`instance.py`), construída a partir da lista de arestas `a`. `greedy.py` e
`tabu_search.py` passaram a usar `instance.affinity`.

**Por quê:** greedy/tabu acessam `affinity[i][j]` (matriz), mas `instance.a` é uma lista de triplas.
Indexar uma tripla por um id de pessoa estourava `IndexError`. A matriz com `@cached_property`
constrói uma vez e reaproveita — sem custo repetido.

**Resultado verificado:** oma01 greedy 450 → tabu 468 (tamanho de grupo = `m`, correto).

---

## 4. Limpeza de código (legibilidade)

**O que:** refatoração com nomes semânticos e remoção de comentários ruidosos:

- `greedy.py` / `tabu_search.py`: `group`, `affinity_gain`, `leaving`/`entering`, `tabu_until`;
  helpers `_swap_delta` e `_random_perturbation` extraídos. Comportamento do algoritmo preservado.
- `model.py`: removidos comentários em português soltos, `x`/`z` → `selected`/`paired`, laços de
  restrição unificados.

**Por quê:** o código tinha comentários redundantes e variáveis de uma letra; nomes semânticos
facilitam a leitura e a manutenção sem mudar a lógica.

---

## 5. Log de **todas** as sementes (JSONL)

**O que:** a metaheurística passou a **persistir cada execução de cada semente**, não só a melhor.
Função `append_meta_run` (`logger.py`) grava **uma linha JSON por semente** em
`logs/omaNN_tabu.jsonl`. O tempo passou a ser medido **por semente**.

**Por quê:** requisito explícito — "obrigatoriamente salvar tudo". A análise estatística (média,
desvio-padrão) exige todas as réplicas, não apenas o melhor valor.

**Formato escolhido:** JSONL (uma linha por execução), apenas métricas
(`seed, initial_solution, final_solution, time_ms` + identificação) — decisão do usuário (sem os
membros do grupo).

---

## 6. Histórico acumulativo entre execuções

**O que:** `append_meta_run` abre o arquivo em modo **append** (sem truncar). Reexecutar acrescenta
linhas em vez de sobrescrever.

**Por quê:** o usuário quer manter o histórico de todas as vezes que rodou. Para recomeçar do zero,
basta apagar a pasta/arquivo da configuração antes.

**Resultado verificado:** duas execuções de 3 sementes → 6 linhas (histórico preservado).

---

## 7. Logging estruturado de eventos (+ arquivo por padrão)

**O que:** um `logger = Logger(...)` no nível do módulo emite eventos estruturados em JSON ao longo
do `main.py` (`get_arguments.*`, `run_one.*`, `run_metaheuristic.*`, `main.*`). Os eventos vão para
**stderr e para `logs/events.log`** por padrão.

**Por quê:** "queremos saber o que está acontecendo". Eventos estruturados (event_kind + data)
permitem rastrear cada passo e depurar sem poluir a saída humana (resumos via `print` ficam no
stdout; eventos no stderr/arquivo, cleanly separáveis).

**Detalhe técnico:** `Logger.__init__` cria o diretório do arquivo de log (`os.makedirs`) antes de
anexar o `FileHandler`, pois o logger é instanciado no import (antes de `logs/` existir).

---

## 8. Reconciliação da **baseline** (decisão data-backed)

**O que:** os parâmetros padrão da Busca Tabu em `main.py` foram alinhados à baseline documentada:
`DEFAULT_TABU = tenure=10, max_no_improve=100, max_iter=1000, diversify_freq=50` (= defaults de
`tabu_search.py` e de [`parameters.md`](parameters.md)). Antes o código usava `15/1000/10000/150`.

**Por quê:** as varreduras de sensibilidade variam **um** parâmetro por vez mantendo os demais na
baseline. Os valores antigos (a) estavam **fora** das faixas do catálogo (`max_iter=10000` > 5000;
`max_no_improve=1000` > 800) e (b) descentravam todas as curvas. Uma baseline **não** é "o melhor
conjunto" — é o **centro de referência** das varreduras; os melhores parâmetros saem do experimento
(viram a config `B_tuned`).

**Evidência coletada** (5 sementes, in-memory):

| config | oma01 médio (melhor) | oma10 médio (melhor) | tempo/semente |
|---|---|---|---|
| baseline 10/100/1000/50 | 468.0 (472) | 704.8 (716) | 0.17–0.35s |
| antigo 15/1000/10000/150 | 469.8 (472) | 714.0 (**721**) | 1.5–3.2s |
| meio 10/200/2000/50 | 470.4 (472) | 704.8 (716) | 0.4–0.6s |

O esforço maior ajuda nas instâncias grandes (oma10: 721 vs 716) — e é exatamente isso que as
varreduras A2 (paciência até 800) e A3 (`max_iter` até 5000) existem para descobrir. Por isso a
baseline fica leve/central e o sweep encontra o ponto bom para `B_tuned`.

---

## 9. Runner com parâmetros via **linha de comando**

**O que:** o parser manual virou **argparse** (`main.py`), com flags de ajuste que default-am para
a baseline:

```
--tenure --max-iter --max-no-improve --diversify-freq --seeds --init {greedy,random}
--config-id --out-dir
```

Cada linha do `.jsonl` passou a embutir `params` + `config_id`, e a saída é roteada para
`<out-dir>/<config_id>/omaNN_tabu.jsonl`. Um `config.json` por configuração é escrito
(`write_config`), tornando cada pasta de resultados autoexplicativa.

**Por quê (três motivos):**
1. **Requisito do enunciado** ([`specification.md`](specification.md)): os principais parâmetros do
   método devem ser definíveis por linha de comando. Antes ficavam fixos no código.
2. **Rastreabilidade**: antes as linhas do `.jsonl` não gravavam parâmetros e todas as configs
   escreviam no mesmo arquivo (colidiam). Agora cada resultado é autodescritivo e isolado por
   `config_id`.
3. **Operação**: elimina editar o código 31 vezes e mover arquivos à mão — cada máquina roda uma
   lista de comandos.

**Bônus (bloco A5):** adicionada `random_construction` (`greedy.py`) — escolhe `m` pessoas ao acaso
— para suportar a variante "solução inicial aleatória", que antes não existia no código.

---

## 10. Listas de comandos por máquina

**O que:** geradas a partir do catálogo de [`test_division.md`](test_division.md):

- `docs/run_M1.sh` — Gabriel (PC-A): A1 (tenure, 9) + A5 (init, 2) = **11 configs**.
- `docs/run_M2.sh` — Gabriel (PC-B): A3 (max_iter, 5) + B (3) + **solver HiGHS** = 8 + solver.
- `docs/run_M3.sh` — Rodrigo: A2 (max_no_improve, 6) + A4 (diversify_freq, 6) = **12 configs**.

Cada máquina usa uma `--out-dir` própria (`results/M1`, `results/M2`, `results/M3`) para evitar
colisão na hora do merge.

**Por quê:** divide ~31 configs equilibradamente (o bloco A3, mais pesado, fica isolado com B em
M2) e mantém os resultados rastreáveis por configuração.

> **Atenção:** `B_tuned` em `run_M2.sh` é **placeholder** — seus valores só podem ser fixados após
> analisar as varreduras A1–A4. Rodar por último.

---

## 11. Correções de documentação

- [`test_division.md`](test_division.md): §4/§6 reescritas (procedimento manual → runner
  automatizado); corrigido exemplo de `config.json` (`diversify_freq` 150 → 50).
- [`specification.md`](specification.md): removidas notas desatualizadas ("registra apenas a melhor
  réplica" e "params fixos no código") — ambas já resolvidas.

---

## Arquivos alterados / criados

| Arquivo | Mudança |
|---|---|
| `src/oma/main.py` | argparse, 3 modos, baseline `DEFAULT_TABU`, runner com flags, logging de eventos |
| `src/oma/instance.py` | propriedade `affinity` (matriz n×n com cache) |
| `src/oma/logger.py` | `append_meta_run` (JSONL + params + config_id + roteamento), `write_config`, `Logger` cria diretório |
| `src/oma/solvers/generic.py` | `create(solver_type, time_limit)` parametrizado |
| `src/oma/solvers/model.py` | limpeza (nomes `selected`/`paired`) |
| `src/oma/metaheuristica/greedy.py` | limpeza + `random_construction` (A5) |
| `src/oma/metaheuristica/tabu_search.py` | correção (`instance.affinity`) + limpeza |
| `docs/run_M1.sh`, `run_M2.sh`, `run_M3.sh` | listas de comandos por máquina (novos) |
| `docs/test_division.md`, `docs/specification.md` | correções/atualizações |

---

## Como rodar (referência rápida)

```bash
uv sync                                   # instala pulp + highspy (CPLEX NÃO é necessário p/ heurística)

# Modos:
uv run oma all --tabu                     # metaheurística em todas as instâncias
uv run oma all --highs                    # solver exato em todas
uv run oma all --cplex --tabu             # solver e depois metaheurística

# Varredura completa (uma máquina):
bash docs/run_M1.sh                       # idem run_M2.sh / run_M3.sh

# Config avulsa com parâmetros:
uv run oma all --tabu --tenure 5 --max-iter 2000 --config-id A1_tenure-05 --out-dir results/M1
```

Saídas:
- `results/<maquina>/<config_id>/omaNN_tabu.jsonl` — uma linha por semente (com `params` + `config_id`).
- `results/<maquina>/<config_id>/config.json` — parâmetros da configuração.
- `logs/omaNN_<cplex|highs>.json` — resultado do solver exato (status, objetivo, tempo).
- `logs/events.log` — trilha de eventos estruturados.

---

## Notas de ambiente e verificação

- **CPLEX** não está instalado nesta máquina (caminho fixo
  `/opt/ibm/ILOG/CPLEX_Studio222/...`); rodar `--cplex` exige a máquina com o binário. A heurística
  e o HiGHS **não** precisam de CPLEX.
- As mudanças de heurística/logger/argparse foram **validadas diretamente** (a metaheurística não
  depende do solver). O caminho `uv run oma` completo não pôde ser executado aqui (sem `uv`/`pulp`
  nesta máquina) — fazer um smoke test antes do sweep:
  `uv run oma 1 --tabu --config-id smoke --out-dir /tmp/t`.

## Pendências conhecidas

- **Agregação estatística** (média/desvio por instância×config a partir da árvore `results/**`) e a
  tabela final do relatório — ainda não implementadas.
- **`B_tuned`** — definir os valores após analisar A1–A4.
- **Convenção de I/O do enunciado** (stdin para instância, stdout para solução, 1º argumento =
  arquivo de saída) — fora do escopo até aqui.

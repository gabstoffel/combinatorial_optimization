# Plano — Módulo Agregador + Gráficos (matplotlib)

## Contexto

As varreduras (M1/M2/M3) e o solver produzem uma árvore de resultados **method-first**:
metaheurística em `results/metaheuristica/tabu/<maquina>/<config_id>/omaNN_tabu.jsonl` (uma linha
por semente) e solver em `results/solver/<solver>/<maquina>/<config_id>/omaNN_<solver>.jsonl` (uma
linha por instância). Cada linha é **autodescritiva** (`params`, `config_id`); `solver`/`maquina`
também são deriváveis do caminho. Falta o passo de **análise**: consolidar essas estatísticas e
gerar as **tabelas** e **gráficos** que o relatório exige.

A estrutura do relatório segue [`reference_report.md`](reference_report.md) (seções 7 e 8) e
[`test_plan.md`](test_plan.md). Os melhores valores conhecidos estão em [`bkv.md`](bkv.md).

Objetivo: um **novo módulo** (`src/oma/analysis/`) que consome os `.jsonl`, calcula as métricas
derivadas e gera os gráficos com **matplotlib** + as tabelas do relatório.

---

## 1. Fontes de dados

| Fonte | Conteúdo |
|---|---|
| `results/**/omaNN_tabu.jsonl` | metaheurística: `instance, method, config_id, seed, params{tenure,max_no_improve,max_iter,diversify_freq,init}, initial_solution, final_solution, time_ms` |
| `results/**/omaNN_{highs,cplex}.jsonl` | solver: `instance, method, config_id, status, params, final_solution, time_ms` (sem `seed`/`initial_solution`) |
| `results/**/config.json` | parâmetros da config (redundante com `params`, usado como rótulo) |
| [`bkv.md`](bkv.md) | BKV por instância (oma01..oma10) → vira constante `BKV` no módulo |

O **bloco** de cada config (A1..A5, B) e o valor do parâmetro variado são derivados do
`config_id` (`A1_tenure-05` → bloco `A1`, tenure=5) e confirmados via `params`.

---

## 2. Métricas (test_plan.md §3)

Por execução: **SI** (`initial_solution`), **SF** (`final_solution`), **tempo** (`time_ms`).
Derivadas:
- `dev_initial_pct = 100·(SI − SF)/SI`  (≤ 0; maximização ⇒ SF ≥ SI)
- `dev_bkv_pct = 100·(BKV − SF)/BKV`  (quanto menor, mais perto do ótimo)
- `otimalidade_pct = 100·SF/BKV`  (usado nos gráficos de sensibilidade)

Agregação por **(config_id, instância)**: média/desvio-padrão de SF e tempo sobre as sementes,
melhor SF (e a semente correspondente). Agregação por **config_id**: média de `otimalidade_pct` e
de tempo sobre as 10 instâncias (base das curvas de sensibilidade).

---

## 3. Gráficos necessários (entregável principal)

Mapeados à especificação. Todos salvos em `report/figures/*.png` (+ `.pdf` opcional).

### Sensibilidade — 1 figura por parâmetro (referência §7, test_plan §4)
Eixo X = valor do parâmetro; **eixo Y1** = otimalidade média (%) com barra de erro (desvio sobre
sementes×instâncias); **eixo Y2** (segundo eixo) = tempo médio (ms). Mesma forma das Figuras 1–4
do relatório de referência (qualidade × parâmetro, em paralelo com tempo × parâmetro).

| ID | Arquivo | Bloco | X (valores) |
|----|---------|-------|-------------|
| G1 | `A1_tenure.png` | A1 | tenure ∈ 1,3,5,7,10,15,20,30,50 |
| G2 | `A2_max_no_improve.png` | A2 | 25,50,100,200,400,800 |
| G3 | `A3_max_iter.png` | A3 | 250,500,1000,2000,5000 |
| G4 | `A4_diversify_freq.png` | A4 | 0,10,25,50,100,200 |

### A5 — construção inicial (referência §8 / test_plan §4)
| ID | Arquivo | Tipo |
|----|---------|------|
| G5 | `A5_init.png` | barras: SI e SF médios para `greedy` vs `random` (mostra o ganho do greedy na SI e a convergência da SF) |

### Comparação por instância (referência §8.5, Figuras 5–8; test_plan §5)
| ID | Arquivo | Tipo |
|----|---------|------|
| G6 | `B_instances_quality.png` | barras agrupadas por instância (oma01..10): `otimalidade_pct` de **baseline / tunada / degenerada / solver**, com linha de referência BKV = 100% |
| G7 | `B_instances_time.png` | barras agrupadas: tempo MH (por config) vs tempo solver, por instância (escala log se necessário) |

> Total: **7 figuras** (4 de sensibilidade + A5 + 2 de comparação). G6/G7 podem ser quebradas em
> subfiguras por grupos de instâncias se ficarem densas, espelhando as Figuras 5–8 da referência.

---

## 4. Tabelas necessárias (test_plan §5 e §7)

Salvas em `report/tables/` em **CSV** (máquina) e **Markdown** (colar no relatório).

- **T1 — por configuração B** (uma por baseline/tunada/degenerada; referência Tabelas 2–4):
  `Instância | SI | SF | Desvio SI % | Desvio BKV % | Tempo MH (ms) | Tempo Solver (ms) | Semente`.
- **T2 — solver** (referência Tabela 5): `Instância | BKV | Obtido | Desvio BKV % | Status | Tempo (ms)`.
- **`report/aggregated.json`** (schema do test_plan §7): por (instância, config) com
  `final_solution_mean/std`, `dev_bkv_pct_mean`, `time_ms_mean`, `replications`.

---

## 5. Arquitetura do módulo

Novo pacote `src/oma/analysis/`:

| Arquivo | Responsabilidade |
|---|---|
| `bkv.py` | constante `BKV = {1:472, …, 10:721}` (fonte: `bkv.md`) |
| `load.py` | varre `--results-dir` (glob `results/**/*.jsonl`), lê todos os `.jsonl`, normaliza (meta vs solver por presença de `seed`/`status`; `family`/`solver`/`maquina` derivados do caminho `results/<family>/<method>/<maquina>/<config>`), anexa bloco/param/BKV |
| `aggregate.py` | métricas derivadas + agregações por (config,instância) e por config; gera `aggregated.json` e os CSV/MD de tabela |
| `plots.py` | funções matplotlib: `sensitivity_plot(block)`, `init_comparison()`, `instance_comparison()` (G1–G7) |
| `report.py` | CLI `oma-report`: orquestra load → aggregate → plots → tables; cria `report/figures`, `report/tables`, `aggregated.json` |

**Entrada/saída do CLI:**
```bash
uv run oma-report --results-dir results --out-dir report
# opções: --configs baseline=B_baseline,tuned=B_tuned,degenerate=B_degenerate
#         --solver-method highs
```
Rótulos de config "baseline/tunada/degenerada" e qual é o solver são passados por flag (ou
inferidos por convenção de `config_id`), para não fixar nomes no código.

**Dependências:** adicionar `matplotlib` (puxa `numpy`) ao `pyproject.toml`; novo console script
`oma-report = "oma.analysis.report:main"`.

---

## 6. Pré-requisitos de dados (ações fora do módulo)

- **Solver na árvore:** rodar os scripts de máquina (`run_M1.sh`, `run_M2.sh`, `run_M3.ps1`) — cada
  um cobre sua fatia de instâncias (oma01-04 / oma05-07 / oma08-10) com HiGHS + CPLEX, roteando
  para `results/solver/<solver>/<maquina>/tl-600/omaNN_<solver>.jsonl` com campo `status` por
  instância (Optimal/Feasible). As 10 instâncias de cada solver ficam espalhadas pelas pastas
  M1/M2/M3 — o glob `results/**` as reúne. O solver é **determinístico**: 1 linha por instância,
  independente das sementes da metaheurística.
- **`B_tuned`** depende da análise de A1–A4; G1–G4 devem ser geradas antes para escolher os
  valores tunados.
- Merge das três máquinas numa única árvore `results/` antes de rodar o `oma-report`.

---

## 7. Verificação

1. `uv run oma-report --results-dir results --out-dir report` gera, sem erro, as 4 figuras de
   sensibilidade disponíveis (A1 já existe no M1) + `aggregated.json` + CSVs.
2. Conferir números contra a checagem manual já feita (M1: gap total ~0,18% vs BKV; pico de
   `tenure` em 15–20) — as curvas devem refletir isso.
3. `aggregated.json` valida no schema do test_plan §7 (chaves e tipos).
4. Robustez: rodar com apenas o M1 presente não deve quebrar (blocos ausentes → figura pulada com
   aviso, não erro).
5. Sem efeitos colaterais na pasta `results/` (somente leitura); tudo escrito em `report/`.

## Fora de escopo (não fazer agora)
- Geração do PDF/relatório final (só as figuras + tabelas que serão coladas nele).
- Saída dos **membros** da melhor solução (convenção §6 do enunciado) — pendência separada.

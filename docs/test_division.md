# Divisão dos Testes — 3 máquinas

Plano para dividir as execuções do [`test_plan.md`](test_plan.md) entre **3 máquinas**:
dois PCs do Gabriel (M1, M2) e o PC do Rodrigo (M3). O objetivo é equilibrar o tempo de
parede e manter os resultados rastreáveis por configuração.

## 1. Pré-requisitos (combinar antes de rodar)

- **Baseline única** (fixar igual em todas as máquinas, em `TABU_PARAMS` no `main.py`):
  `tenure=10`, `max_no_improve=100`, `max_iter=1000`, `diversify_freq=50`. Os varreduras
  abaixo partem dela. *(Hoje o código está com 15/1000/10000/150 — alinhar antes de começar.)*
- **Sementes**: todas as máquinas usam as mesmas 5 sementes (`META_SEEDS=5` → sementes 0–4).
  Como tudo é determinístico, cada configuração é totalmente reproduzível.
- **Unidade de trabalho = uma configuração inteira** (10 instâncias × 5 sementes = 50 linhas).
  Nunca dividir as sementes de uma mesma configuração entre máquinas — mantém o `.jsonl` coeso.

## 2. Catálogo de configurações (31 no total)

Cada configuração varia **um** parâmetro, mantendo os demais na baseline. Cada uma gera 50
linhas de resultado (10 instâncias × 5 sementes).

| Bloco | Parâmetro variado | Valores | Nº de configs |
|-------|-------------------|---------|--------------:|
| A1 | `tenure` | 1, 3, 5, 7, 10, 15, 20, 30, 50 | 9 |
| A2 | `max_no_improve` | 25, 50, 100, 200, 400, 800 | 6 |
| A3 | `max_iter` | 250, 500, 1000, 2000, 5000 | 5 |
| A4 | `diversify_freq` | 0, 10, 25, 50, 100, 200 | 6 |
| A5 | solução inicial | greedy, aleatória | 2 |
| B  | configuração completa | baseline, tunada, degenerada | 3 |

Solver exato: 1 execução cobrindo as 10 instâncias (`uv run oma --highs all`).

## 3. Atribuição por máquina

Equilibrado pelo esforço aproximado (peso ∝ `max_iter` efetivo × nº de execuções). A3 é o bloco
mais pesado (inclui `max_iter=5000`), por isso vai sozinho com o bloco B.

| Máquina | Responsável | Blocos | Configs | Observação |
|---------|-------------|--------|--------:|------------|
| M1 | Gabriel (PC-A) | A1 + A5 | 11 | Varredura de `tenure` + solução inicial |
| M2 | Gabriel (PC-B) | A3 + B + **solver** | 8 + solver | Bloco mais pesado (`max_iter` alto) + tabela final |
| M3 | Rodrigo | A2 + A4 | 12 | `max_no_improve` + `diversify_freq` |

Total: 31 configs de metaheurística (1550 execuções) + 1 rodada de solver (10 execuções).

## 4. Procedimento por configuração (automatizado)

O runner já recebe os parâmetros por linha de comando, grava cada linha do `.jsonl` **com os
parâmetros e o `config_id` embutidos**, roteia a saída para `<out-dir>/<config_id>/` e escreve um
`config.json` por configuração. Não é mais preciso editar `main.py` nem mover arquivos.

Cada máquina só executa sua lista de comandos (uma linha por config):

```bash
bash docs/run_M1.sh      # M1 (A1 + A5)
bash docs/run_M2.sh      # M2 (A3 + B + solver)
bash docs/run_M3.sh      # M3 (A2 + A4)
```

Forma de cada comando (parâmetro variado explícito; os demais caem na baseline por padrão):

```bash
uv run oma all --tabu --tenure 5 --config-id A1_tenure-05 --out-dir results/M1
```

`config_id` segue o padrão `A1_tenure-05`, `A3_maxiter-5000`, `B_baseline`, etc. Rodar a mesma
config de novo **acrescenta** linhas (histórico) — para recomeçar do zero, apague a pasta da
config antes.

## 5. Coleta e merge dos resultados

- Cada máquina usa uma pasta-raiz distinta para evitar colisão: `results/M1/...`, `results/M2/...`,
  `results/M3/...`.
- Ao final, juntar tudo num só lugar (commit no git numa branch de resultados ou pasta
  compartilhada). A estrutura final fica `results/<maquina>/<config_id>/omaNN_tabu.jsonl` +
  `config.json`.
- A agregação (média e desvio-padrão por instância/configuração) e as tabelas/gráficos do
  relatório são geradas a partir dessa árvore.

## 6. Automação (implementada)

✅ Feito. O runner aceita os parâmetros por linha de comando
(`--tenure/--max-iter/--max-no-improve/--diversify-freq/--seeds/--init`), embute `params` +
`config_id` em cada linha do `.jsonl` e roteia a saída via `--config-id` + `--out-dir`. As listas
prontas de comandos por máquina estão em `docs/run_M1.sh`, `docs/run_M2.sh`, `docs/run_M3.sh`.

> Pendente de decisão da equipe: os valores da config **B_tuned** (a "tunada") só podem ser
> fixados depois de analisar as varreduras A1–A4 — rodar B_tuned por último (ver `run_M2.sh`).

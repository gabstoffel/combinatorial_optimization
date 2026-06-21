# Melhorias de código

Este documento reúne sugestões para deixar o código mais legível, consistente e
idiomático. O ponto de partida foi o dispatch de construtores em `main.py`:

```python
CONSTRUCTORS = {"greedy": greedy_construction, "random": random_construction}
```

Cada item segue o formato **Problema → Por quê → Sugestão**, com exemplos de
antes/depois. As referências de arquivo:linha apontam para o estado atual do
código.

---

## 1. Trocar o dict `CONSTRUCTORS` por um enum

**Problema.** O método de construção é escolhido por um dict de strings
(`main.py:26`, usado em `main.py:155`) e as mesmas strings ainda aparecem soltas
no argumento `--init` (`main.py:47`). Não há tipagem nem um ponto único de verdade.

**Por quê.** O projeto já resolve um caso idêntico com enum: `SolverType` +
`GenericSolver.create` em `src/oma/solvers/generic.py`. Usar um enum aqui também
mantém o estilo consistente, evita strings repetidas e torna o dispatch tipado.

**Sugestão.** Definir um enum ao lado dos construtores, em
`src/oma/metaheuristica/greedy.py`, com um método que encapsula o dispatch:

```python
# greedy.py
from enum import Enum


class ConstructionMethod(Enum):
    GREEDY = "greedy"
    RANDOM = "random"

    def build(self, instance: Instance) -> list[int]:
        if self is ConstructionMethod.GREEDY:
            return greedy_construction(instance)
        return random_construction(instance)
```

No `main.py`, o CLI passa a derivar as escolhas do próprio enum e a guardar o
enum já convertido:

```python
# build_parser()
parser.add_argument(
    "--init",
    choices=[method.value for method in ConstructionMethod],
    default=ConstructionMethod.GREEDY.value,
    help="construção da solução inicial da metaheurística",
)

# parse_args()
args.init = ConstructionMethod(args.init)
```

E o `run_metaheuristic` deixa de consultar o dict:

```python
# antes
construct = CONSTRUCTORS[init]
...
initial = construct(instance)

# depois
initial = init.build(instance)
```

Com isso o dict global `CONSTRUCTORS` desaparece.

---

## 2. Suavizar comentários "numerados" e autorreferentes

**Problema.** Alguns comentários soam mecânicos:

- `# Mode 1/3:` e `# Mode 2/3:` (`main.py:237`, `main.py:243`)
- `# Documented sweep baseline (parameters.md == tabu_search.py defaults).`
  (`main.py:22`)

**Por quê.** Numeração do tipo "x/3" e comentários que se referem a outros
arquivos com `==` chamam atenção e não ajudam quem lê o código.

**Sugestão.** Preferir comentários curtos e naturais, ou remover quando o código
já se explica:

```python
# antes
# Mode 1/3: run the chosen solver over all targets first.
if args.solver_option is not None:

# depois
# Primeiro o solver exato, depois a metaheurística.
if args.solver_option is not None:
```

---

## 3. Substituir a cadeia de ternários no dispatch do solver

**Problema.** A escolha do solver usa ternários aninhados (`main.py:75-77`):

```python
args.solver_option = (
    SolverType.CPLEX if args.cplex else SolverType.HIGHS if args.highs else None
)
```

**Por quê.** Ternário encadeado é denso e difícil de ler de relance.

**Sugestão.** Um `if/elif` explícito deixa as três possibilidades óbvias:

```python
if args.cplex:
    args.solver_option = SolverType.CPLEX
elif args.highs:
    args.solver_option = SolverType.HIGHS
else:
    args.solver_option = None
```

---

## 4. Padronizar a criação de dicionários

**Problema.** O código mistura `dict(...)` e literais `{...}`:

- `DEFAULT_TABU = dict(tenure=10, ...)` (`main.py:23`)
- `args.tabu_params = dict(tenure=..., ...)` (`main.py:79`)
- `logged_params = {**tabu_params, "init": init}` (`main.py:145`)

**Por quê.** Misturar os dois estilos é inconsistente e dá a impressão de código
montado de pedaços diferentes.

**Sugestão.** Escolher um estilo (literais `{}`) e aplicá-lo em todos os pontos.
Opcionalmente, encapsular os parâmetros do tabu num `dataclass` para dar tipo e
nome ao conjunto:

```python
from dataclasses import dataclass


@dataclass
class TabuParams:
    tenure: int = 10
    max_no_improve: int = 100
    max_iter: int = 1000
    diversify_freq: int = 50
```

---

## 5. (Opcional / arriscado) Nomes de eventos de log estruturados

**Observação.** As chamadas como `logger.info("run_one.start", {...})` usam nomes
de evento "pontuados" (`run_one.start`, `run_metaheuristic.seed_done`, ...) que
têm cara de código gerado.

**Cuidado.** Os documentos em `docs/` e os arquivos em `logs/` podem depender
desses nomes para parsing e geração de relatórios. **Renomear pode quebrar essa
cadeia.** Tratar como melhoria opcional e de baixa prioridade — só mexer depois de
confirmar que nada consome esses nomes.

---

## 6. Organizar as constantes de topo de módulo

**Problema.** O bloco de globais em `main.py:14-26` mistura caminho de log,
constantes numéricas, defaults do tabu e o dict de construtores.

**Sugestão.** Agrupar por finalidade com comentários enxutos e mover defaults para
perto de quem os usa quando fizer sentido (ex.: os defaults do tabu junto da
definição de `TabuParams`, item 4). Com os itens 1 e 4 aplicados, `CONSTRUCTORS` e
`DEFAULT_TABU` saem daqui.

---

## Prioridade

| Ordem | Item | Impacto | Risco |
|-------|------|---------|-------|
| 1 | (1) Enum `ConstructionMethod` | Alto | Baixo |
| 2 | (3) Remover ternário aninhado | Médio | Baixo |
| 3 | (2) Comentários mais naturais | Médio | Baixo |
| 4 | (4) Padronizar dicts / `TabuParams` | Médio | Baixo |
| 5 | (6) Organizar globais | Baixo | Baixo |
| 6 | (5) Renomear eventos de log | Baixo | **Alto** |

Recomendação: começar por (1) e (3) — alto retorno e baixo risco — e deixar (5)
por último, só se for seguro.

"""Resolve uma instância do OMA lida da entrada padrão.

A instância é lida da stdin, o primeiro argumento é o arquivo onde a melhor
solução é gravada (também impressa na stdout) e os parâmetros vêm da linha de
comando. O modo padrão é a Busca Tabu; --highs/--cplex resolvem o modelo exato.

    oma-solve <arquivo_saida> [--tabu | --highs | --cplex] [parâmetros] < instancia.dat

A saída tem duas linhas: o valor objetivo e os índices selecionados (base 0).
"""

import argparse
import random
import sys

from oma.instance import Instance
from oma.metaheuristica.greedy import greedy_construction, random_construction
from oma.metaheuristica.tabu_search import run_tabu_search
from oma.solvers import GenericSolver, SolverType, build_model, selected_indices

CONSTRUCTORS = {"greedy": greedy_construction, "random": random_construction}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="oma-solve",
        description="Resolve uma instância do OMA lida da entrada padrão (stdin) "
                    "e grava a melhor solução no arquivo de saída e na stdout.",
    )
    # 1º argumento posicional: arquivo onde gravar a melhor solução (convenção do trabalho).
    parser.add_argument("output", help="arquivo para gravar a melhor solução encontrada")

    # Escolha do método (padrão: meta-heurística Busca Tabu).
    parser.add_argument("--tabu", action="store_true",
                        help="usar a meta-heurística Busca Tabu (padrão)")
    parser.add_argument("--highs", action="store_true", help="resolver o modelo exato com HiGHS")
    parser.add_argument("--cplex", action="store_true", help="resolver o modelo exato com CPLEX")

    # Parâmetros da meta-heurística.
    parser.add_argument("--tenure", type=int, default=10)
    parser.add_argument("--max-iter", type=int, default=1000)
    parser.add_argument("--max-no-improve", type=int, default=100)
    parser.add_argument("--diversify-freq", type=int, default=50)
    parser.add_argument("--init", choices=("greedy", "random"), default="greedy",
                        help="construção da solução inicial da meta-heurística")
    parser.add_argument("--seed", type=int, default=0,
                        help="semente do gerador aleatório (meta-heurística)")

    # Parâmetro do solver exato.
    parser.add_argument("--time-limit", type=int, default=600,
                        help="tempo-limite do solver exato, em segundos")

    return parser


def parse_args(argv):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.highs and args.cplex:
        parser.error("escolha apenas um solver exato (--highs ou --cplex)")
    if (args.highs or args.cplex) and args.tabu:
        parser.error("escolha a meta-heurística (--tabu) OU um solver exato, não ambos")

    return args


def solve_with_tabu(instance: Instance, args) -> tuple[float, list[int]]:
    """Roda a Busca Tabu (construção inicial + busca) e devolve (objetivo, índices)."""
    random.seed(args.seed)
    construct = CONSTRUCTORS[args.init]
    initial = construct(instance)
    group, objective = run_tabu_search(
        instance=instance,
        initial_solution=initial,
        max_iter=args.max_iter,
        max_no_improve=args.max_no_improve,
        tenure=args.tenure,
        diversify_freq=args.diversify_freq,
    )
    return objective, sorted(group)


def solve_with_solver(instance: Instance, solver_type: SolverType, time_limit: int
                      ) -> tuple[float, list[int]]:
    """Resolve o modelo inteiro exato e devolve (objetivo, índices selecionados)."""
    problem = build_model(instance)
    solver = GenericSolver.create(solver_type, time_limit=time_limit)
    problem.solve(solver)
    indices = selected_indices(problem, instance.n)
    objective = problem.objective.value()
    return objective, indices


def format_solution(objective: float, indices: list[int]) -> str:
    """Formata a solução: linha 1 com o objetivo, linha 2 com os índices."""
    # Objetivo inteiro é impresso sem casas decimais.
    if objective is not None and float(objective).is_integer():
        objective_str = str(int(objective))
    else:
        objective_str = str(objective)
    indices_str = " ".join(str(i) for i in indices)
    return f"{objective_str}\n{indices_str}\n"


def write_solution(path: str, objective: float, indices: list[int]) -> None:
    """Grava a melhor solução no arquivo de saída e também na stdout."""
    text = format_solution(objective, indices)
    with open(path, "w") as file:
        file.write(text)
    sys.stdout.write(text)


def main():
    args = parse_args(sys.argv[1:])

    instance = Instance.from_stream(sys.stdin)

    if args.highs or args.cplex:
        solver_type = SolverType.HIGHS if args.highs else SolverType.CPLEX
        objective, indices = solve_with_solver(instance, solver_type, args.time_limit)
    else:
        objective, indices = solve_with_tabu(instance, args)

    write_solution(args.output, objective, indices)


if __name__ == "__main__":
    main()

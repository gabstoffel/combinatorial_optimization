import sys
import time

from pulp import LpStatus

from oma.instance import Instance
from oma.logger import write_run, Logger
from oma.solvers import GenericSolver, SolverType, build_model
from oma.metaheuristica.greedy import greedy_construction
from oma.metaheuristica.tabu_search import run_tabu_search


paths = [
    "dataset/oma01.dat",
    "dataset/oma02.dat",
    "dataset/oma03.dat",
    "dataset/oma04.dat",
    "dataset/oma05.dat",
    "dataset/oma06.dat",
    "dataset/oma07.dat",
    "dataset/oma08.dat",
    "dataset/oma09.dat",
    "dataset/oma10.dat"
]


def getArguments(argv):
    if len(argv) < 3:
        return None, None

    instance_number = int(argv[2])
    solver_option = SolverType(argv[1].removeprefix("--"))

    return instance_number, solver_option


def run_solver(instance_number, solver_option):
    instance = Instance.from_file(instance_number)

    prob = build_model(instance)
    solver = GenericSolver.create(solver_option, time_limit=1800)

    start = time.perf_counter()
    prob.solve(solver)
    elapsed_ms = (time.perf_counter() - start) * 1000

    write_run(
        instance_number=instance_number,
        method=solver_option.value,
        final_solution=prob.objective.value(),
        time_ms=elapsed_ms,
    )

    print(f"\n[EXATO] instance: oma{instance_number:02d}")
    print(f"status:    {LpStatus[prob.status]}")
    print(f"objective: {prob.objective.value()}")
    print(f"time_ms:   {elapsed_ms:.1f}")


def run_tabu(instance, instance_number):
    for seed in range(5):
        initial_sol = greedy_construction(instance)

        best_sol, best_obj = run_tabu_search(
            instance=instance,
            initial_solution=initial_sol,
            max_iter=10000,
            max_no_improve=1000,
            tenure=15,
            diversify_freq=150
        )

        write_run(
            instance_number=instance_number,
            method="tabu_search",
            final_solution=best_obj,
            time_ms=0,
        )

        print(f"[TABU] instance {instance_number:02d} seed={seed} best={best_obj}")


def main():
    logger = Logger()

    instance_number, solver_option = getArguments(sys.argv)
    
    logger.info("oma.starting", {
        "instance_number": instance_number,
        "solver": solver_option.value
    })

    if instance_number is not None:
        instance = Instance.from_file(instance_number)

        run_solver(instance_number, solver_option)

        run_tabu(instance, instance_number)

        return

    for i, path in enumerate(paths, start=1):
        instance = Instance.from_file(i)

        print(f"\n==============================")
        print(f"Instance {i}: {path}")
        print(f"n={instance.n}, m={instance.m}")

        solver_option = SolverType.HIGHS 
        run_solver(i, solver_option)

        run_tabu(instance, i)


if __name__ == "__main__":
    main()
import sys
import time

from pulp import LpStatus
from oma.instance import Instance
from oma.logger import write_run
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
        raise Exception(
            "Uso: uv run oma --cplex 1"
        )

    instance_number = int(argv[2])
    solver_option = getSolverType(argv[1].removeprefix("--"))

    return instance_number, solver_option


def main():

    instance_number, solver_option = getArguments(sys.argv)
    instance = Instance.from_file(instance_number)

    prob = build_model(instance)
    solver = GenericSolver.create(solver_option)

    start = time.perf_counter()
    prob.solve(solver)
    elapsed_ms = (time.perf_counter() - start) * 1000

    write_run(
        instance_number=number,
        method=solver_option.value,
        final_solution=prob.objective.value(),
        time_ms=elapsed_ms,
    )

    print(f"instance: oma{number:02d} (n={instance.n}, m={instance.m})")
    print(f"status:    {LpStatus[prob.status]}")
    print(f"objective: {prob.objective.value()}")
    print(f"time_ms:   {elapsed_ms:.1f}")
    
    return
    for instance_path in paths:
        instance = load(instance_path)
        logger = Logger(stderr=True)
        logger.info("instance_loaded", {"file": instance_path, "n": instance.n, "m": instance.m})

        for seed in range(5):  # Run multiple times with different random seeds for robustness
            logger.info("run_started", {"seed": seed})
            # início random (antes começava com a pessoa 0)
            initial_sol = greedy_construction(instance)
            logger.info("greedy_done", {"initial_solution": initial_sol})

            # a cada 50 iterações, faz uma perturbação aleatória para escapar de ótimos locais
            best_sol, best_obj = run_tabu_search(
                instance=instance, 
                initial_solution=initial_sol,
                max_iter=10000, 
                max_no_improve=1000, 
                tenure=15,
                diversify_freq=150
            )

            logger.info("tabu_search_finished", {"best_affinity": best_obj, "best_solution": best_sol})

if __name__ == "__main__":
    main()
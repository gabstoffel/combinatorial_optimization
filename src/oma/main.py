import sys
import time

from pulp import LpStatus

from oma.instance import Instance
from oma.logger import write_run
from oma.solvers import GenericSolver, SolverType, build_model
from metaheuristica.greedy import greedy_construction
from metaheuristica.tabu_search import run_tabu_search

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

def main():
    number = 1
    if len(sys.argv) > 1:
        number = int(sys.argv[1])

    instance = Instance.from_file(number)

    prob = build_model(instance)
    solver_type = SolverType.HIGHS
    solver = GenericSolver.create(solver_type)

    start = time.perf_counter()
    prob.solve(solver)
    elapsed_ms = (time.perf_counter() - start) * 1000

    write_run(
        instance_number=number,
        method=solver_type.value,
        final_solution=prob.objective.value(),
        time_ms=elapsed_ms,
    )

    print(f"instance: oma{number:02d} (n={instance.n}, m={instance.m})")
    print(f"status:    {LpStatus[prob.status]}")
    print(f"objective: {prob.objective.value()}")
    print(f"time_ms:   {elapsed_ms:.1f}")
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
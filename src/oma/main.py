import sys
from oma.instance import load
from oma.logger import Logger
from oma.greedy import greedy_construction
from oma.tabu_search import run_tabu_search

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
                max_iter=1000, 
                max_no_improve=150, 
                tenure=12,
                diversify_freq=50
            )

            logger.info("tabu_search_finished", {"best_affinity": best_obj, "best_solution": best_sol})

if __name__ == "__main__":
    main()
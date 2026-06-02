import sys
from oma.instance import load
from oma.logger import Logger
from oma.greedy import greedy_construction
from oma.tabu_search import run_tabu_search

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "dataset/oma01.dat"
    instance = load(path)
    logger = Logger(stderr=True)
    logger.info("instance_loaded", {"file": path, "n": instance.n, "m": instance.m})

    initial_sol = greedy_construction(instance)
    logger.info("greedy_done", {"initial_solution": initial_sol})

    best_sol, best_obj = run_tabu_search(
        instance=instance, 
        initial_solution=initial_sol,
        max_iter=1000, 
        max_no_improve=150, 
        tenure=12
    )

    logger.info("tabu_search_finished", {"best_affinity": best_obj, "best_solution": best_sol})

if __name__ == "__main__":
    main()
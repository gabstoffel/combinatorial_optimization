import argparse
import random
import sys
import time

from pulp import LpStatus

from oma.instance import Instance
from oma.logger import Logger, write_run, append_meta_run, write_config
from oma.solvers import GenericSolver, SolverType, build_model
from oma.metaheuristica.greedy import greedy_construction, random_construction
from oma.metaheuristica.tabu_search import calculate_objective, run_tabu_search

EVENTS_LOG = "logs/events.log"
logger = Logger(file_path=EVENTS_LOG)

NUM_INSTANCES = 10
SOLVER_TIME_LIMIT = 600
META_METHOD = "tabu"

DEFAULT_TABU = dict(tenure=10, max_no_improve=100, max_iter=1000, diversify_freq=50)
DEFAULT_SEEDS = 5

CONSTRUCTORS = {"greedy": greedy_construction, "random": random_construction}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="oma",
        description="OMA exact solver / metaheuristic runner.",
    )
    parser.add_argument("target", help="instance number 1..10, or 'all'")

    parser.add_argument("--cplex", action="store_true", help="run the CPLEX exact solver")
    parser.add_argument("--highs", action="store_true", help="run the HiGHS exact solver")
    parser.add_argument("--tabu", action="store_true", help="run greedy + tabu metaheuristic")

    parser.add_argument("--tenure", type=int, default=DEFAULT_TABU["tenure"])
    parser.add_argument("--max-iter", type=int, default=DEFAULT_TABU["max_iter"])
    parser.add_argument("--max-no-improve", type=int, default=DEFAULT_TABU["max_no_improve"])
    parser.add_argument("--diversify-freq", type=int, default=DEFAULT_TABU["diversify_freq"])
    parser.add_argument("--seeds", type=int, default=DEFAULT_SEEDS, help="number of random seeds")
    parser.add_argument("--init", choices=("greedy", "random"), default="greedy",
                        help="initial-solution construction for the metaheuristic")

    parser.add_argument("--config-id", default=None, help="label embedded in logs + output dir")
    parser.add_argument("--out-dir", default="logs", help="root directory for metaheuristic logs")

    return parser


def parse_args(argv):
    parser = build_parser()
    args = parser.parse_args(argv[1:])

    if not (args.cplex or args.highs or args.tabu):
        parser.error("choose at least one of --cplex / --highs / --tabu")

    if args.target == "all":
        args.instance_number = None
    else:
        try:
            n = int(args.target)
        except ValueError:
            parser.error(f"target must be 1..{NUM_INSTANCES} or 'all', got {args.target!r}")
        if not 1 <= n <= NUM_INSTANCES:
            parser.error(f"target must be 1..{NUM_INSTANCES} or 'all'")
        args.instance_number = n

    args.solver_option = (
        SolverType.CPLEX if args.cplex else SolverType.HIGHS if args.highs else None
    )
    args.use_meta = args.tabu
    args.tabu_params = dict(
        tenure=args.tenure,
        max_no_improve=args.max_no_improve,
        max_iter=args.max_iter,
        diversify_freq=args.diversify_freq,
    )
    return args


def run_one(instance_number: int, solver_option: SolverType):
    logger.info("run_one.start", {
        "instance_number": instance_number,
        "solver": solver_option.value,
        "time_limit_s": SOLVER_TIME_LIMIT,
    })

    instance = Instance.from_file(instance_number)
    logger.info("run_one.instance_loaded", {
        "instance_number": instance_number,
        "n": instance.n,
        "m": instance.m,
        "edges": len(instance.a),
    })

    prob = build_model(instance)
    solver = GenericSolver.create(solver_option, time_limit=SOLVER_TIME_LIMIT)
    logger.info("run_one.solving", {"instance_number": instance_number})

    start = time.perf_counter()
    prob.solve(solver)
    elapsed_ms = (time.perf_counter() - start) * 1000

    status = LpStatus[prob.status]
    objective = prob.objective.value()

    logger.info("run_one.solved", {
        "instance_number": instance_number,
        "status": status,
        "objective": objective,
        "time_ms": elapsed_ms,
    })

    write_run(
        instance_number=instance_number,
        method=solver_option.value,
        final_solution=objective,
        time_ms=elapsed_ms,
        status=status,
        params={"time_limit_s": SOLVER_TIME_LIMIT},
    )

    print(f"[{solver_option.value}] oma{instance_number:02d} (n={instance.n}, m={instance.m})")
    print(f"  status:    {status}")
    print(f"  objective: {objective}")
    print(f"  time_ms:   {elapsed_ms:.1f}")
    print()


def run_metaheuristic(
    instance_number: int,
    tabu_params: dict,
    seeds: int,
    init: str,
    config_id: str | None,
    out_dir: str,
):
    logged_params = {**tabu_params, "init": init}
    logger.info("run_metaheuristic.start", {
        "instance_number": instance_number,
        "config_id": config_id,
        "seeds": seeds,
        "params": logged_params,
    })

    instance = Instance.from_file(instance_number)
    affinity = instance.affinity
    construct = CONSTRUCTORS[init]
    logger.info("run_metaheuristic.instance_loaded", {
        "instance_number": instance_number,
        "n": instance.n,
        "m": instance.m,
    })

    best_obj = -float("inf")
    best_initial = None

    for seed in range(seeds):
        random.seed(seed)

        start = time.perf_counter()
        initial = construct(instance)
        initial_obj = calculate_objective(set(initial), affinity)
        _, obj = run_tabu_search(
            instance=instance,
            initial_solution=initial,
            **tabu_params,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000

        logger.info("run_metaheuristic.seed_done", {
            "instance_number": instance_number,
            "config_id": config_id,
            "seed": seed,
            "initial_solution": initial_obj,
            "final_solution": obj,
            "time_ms": elapsed_ms,
        })

        append_meta_run(
            instance_number=instance_number,
            method=META_METHOD,
            seed=seed,
            initial_solution=initial_obj,
            final_solution=obj,
            time_ms=elapsed_ms,
            params=logged_params,
            config_id=config_id,
            out_dir=out_dir,
        )

        if obj > best_obj:
            best_obj = obj
            best_initial = initial_obj

    logger.info("run_metaheuristic.done", {
        "instance_number": instance_number,
        "config_id": config_id,
        "best_initial": best_initial,
        "best_final": best_obj,
    })

    print(f"[{META_METHOD}] oma{instance_number:02d} (n={instance.n}, m={instance.m})"
          + (f" config={config_id}" if config_id else ""))
    print(f"  seeds:     {seeds} ({init} init)")
    print(f"  best init: {best_initial}")
    print(f"  best:      {best_obj}")
    print()


def main():
    logger.info("main.start", {"argv": sys.argv[1:]})

    args = parse_args(sys.argv)

    targets = (
        list(range(1, NUM_INSTANCES + 1))
        if args.instance_number is None
        else [args.instance_number]
    )
    logger.info("main.config", {
        "targets": targets,
        "solver": args.solver_option.value if args.solver_option else None,
        "use_meta": args.use_meta,
        "config_id": args.config_id,
        "out_dir": args.out_dir,
        "params": {**args.tabu_params, "init": args.init, "seeds": args.seeds},
    })

    if args.solver_option is not None:
        logger.info("main.solver_phase", {"solver": args.solver_option.value, "count": len(targets)})
        for i in targets:
            run_one(i, args.solver_option)

    if args.use_meta:
        logger.info("main.metaheuristic_phase", {"method": META_METHOD, "count": len(targets)})
        write_config(
            {**args.tabu_params, "init": args.init, "seeds": args.seeds},
            config_id=args.config_id,
            out_dir=args.out_dir,
        )
        for i in targets:
            run_metaheuristic(
                i,
                tabu_params=args.tabu_params,
                seeds=args.seeds,
                init=args.init,
                config_id=args.config_id,
                out_dir=args.out_dir,
            )

    logger.info("main.done", {})


if __name__ == "__main__":
    main()

import sys
import time

from pulp import LpStatus

from oma.instance import Instance
from oma.logger import write_run
from oma.solvers import GenericSolver, SolverType, build_model


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


if __name__ == "__main__":
    main()

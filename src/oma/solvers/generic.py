from enum import Enum

from pulp import HiGHS, LpSolver


class SolverType(Enum):
    HIGHS = "highs"


class GenericSolver:
    @staticmethod
    def create(solver_type: SolverType) -> LpSolver:
        match solver_type:
            case SolverType.HIGHS:
                return HiGHS(msg=False)
            case _:
                raise NotImplementedError(
                    f"Solver {solver_type.value} not yet implemented"
                )

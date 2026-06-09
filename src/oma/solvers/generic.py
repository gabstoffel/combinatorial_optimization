from enum import Enum

from pulp import CPLEX_CMD, HiGHS, LpSolver

CPLEX_BINARY_PATH = "/opt/ibm/ILOG/CPLEX_Studio222/cplex/bin/x86-64_linux/cplex"


class SolverType(Enum):
    HIGHS = "highs"
    CPLEX = "cplex"


class GenericSolver:
    @staticmethod
    def create(solver_type: SolverType) -> LpSolver:
        match solver_type:
            case SolverType.HIGHS:
                return HiGHS(msg=False)
            case SolverType.CPLEX:
                return CPLEX_CMD(path=CPLEX_BINARY_PATH, msg=False)
            case _:
                raise NotImplementedError(
                    f"Solver {solver_type.value} not yet implemented"
                )

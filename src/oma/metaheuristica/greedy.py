import random
from oma.instance import Instance

def greedy_construction(instance: Instance, start_person: int = None) -> list[int]:
    """
    Constructs an initial solution using a greedy approach.
    Uses an incremental gains vector to optimize the process.
    
    Args:
        instance: Problem instance
        start_person: Initial person (default: random). Avoids bias from always starting with 0.
    """
    n = instance.n
    m = instance.m
    affinity = instance.a

    solution = set()
    gains = [0.0] * n

    if start_person is None:
        start_person = random.randint(0, n - 1)
    solution.add(start_person)

    for i in range(n):
        if i not in solution:
            gains[i] += affinity[start_person][i]

    while len(solution) < m:
        max_gain = -1.0
        best_person = -1

        for i in range(n):
            if i not in solution:
                if gains[i] > max_gain:
                    max_gain = gains[i]
                    best_person = i

        solution.add(best_person)

        for i in range(n):
            if i not in solution:
                gains[i] += affinity[best_person][i]

    return list(solution)
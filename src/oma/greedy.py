from oma.instance import Instance

def greedy_construction(instance: Instance) -> list[int]:
    """
    Constructs an initial solution using a greedy approach.
    Uses an incremental gains vector to optimize the process.
    """
    n = instance.n
    m = instance.m
    affinity = instance.affinity

    solution = set()
    gains = [0.0] * n

    solution.add(0)

    for i in range(n):
        if i not in solution:
            gains[i] += affinity[0][i]

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
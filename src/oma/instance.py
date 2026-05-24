from dataclasses import dataclass


@dataclass
class Instance:
    n: int
    m: int
    affinity: list[list[float]]


def load(path: str) -> Instance:
    with open(path) as f:
        n, m = map(int, f.readline().split())
        affinity = [[0.0] * n for _ in range(n)]
        for line in f:
            parts = line.split()
            i, j = int(parts[0]), int(parts[1])
            a = float(parts[2])
            affinity[i][j] = a
            affinity[j][i] = a
    return Instance(n=n, m=m, affinity=affinity)

from dataclasses import dataclass
from functools import cached_property


@dataclass
class Instance:
    """
        Representa uma instância do problema OMA.

        n: número de pessoas
        m: tamanho do grupo a selecionar
        a: lista de triplas (i, j, aᵢⱼ) com i < j, uma por aresta,
           espelhando o formato do arquivo .dat
    """
    n: int
    m: int
    a: list[tuple[int, int, float]]

    @cached_property
    def affinity(self) -> list[list[float]]:
        """
        Matriz de afinidade n×n (simétrica) construída a partir de `a`.
        Usada pela metaheurística (greedy + tabu), que indexa affinity[i][j].
        """
        matrix = [[0.0] * self.n for _ in range(self.n)]
        for i, j, aij in self.a:
            matrix[i][j] = aij
            matrix[j][i] = aij
        return matrix

    @staticmethod
    def create_instance(number_of_people, group_size, affinity):
        return Instance(n=number_of_people, m=group_size, a=affinity)

    @classmethod
    def from_lines(cls, lines) -> "Instance":
        """Constrói uma instância a partir de um iterável de linhas no formato
        `.dat`: a primeira linha contém `n m`; as demais, triplas `i j a`
        (com i < j, índices base 0). Linhas em branco são ignoradas.

        Compartilhada por `from_file` e pela leitura via entrada padrão (stdin).
        """
        rows = (line for line in lines if line.strip())

        header = next(rows)
        n, m = header.split()
        n, m = int(n), int(m)

        a = []
        for line in rows:
            i, j, aij = line.split()
            a.append((int(i), int(j), float(aij)))

        return cls(n=n, m=m, a=a)

    @classmethod
    def from_stream(cls, stream) -> "Instance":
        """Lê uma instância de um stream de texto (p.ex. `sys.stdin`)."""
        return cls.from_lines(stream)

    @classmethod
    def from_file(cls, number: int) -> "Instance":
        path = f"dataset/oma{number:02d}.dat"
        with open(path) as file:
            return cls.from_lines(file)

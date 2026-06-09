from dataclasses import dataclass


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

    @staticmethod
    def create_instance(number_of_people, group_size, affinity):
        return Instance(n=number_of_people, m=group_size, a=affinity)

    @classmethod
    def from_file(cls, number: int) -> "Instance":
        path = f"dataset/oma{number:02d}.dat"

        with open(path) as file:
            n, m = file.readline().split()
            n, m = int(n), int(m)

            a = []
            for line in file:
                i, j, aij = line.split()
                a.append((int(i), int(j), float(aij)))

        return cls(n=n, m=m, a=a)

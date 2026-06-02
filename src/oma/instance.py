from dataclasses import dataclass


@dataclass
class Instance:
    """
        representa uma instância do problema, em que 
        n: numero de pessoas
        m: tamanho do conjunto
        affinity: matriz de afinidade entre as pessoas, em que
            a[i][j] é a afinidade entre a pessoa i e a pessoa j
    """
    n: int
    m: int
    a: list[list[float]]
    
    @staticmethod
    def create_instance(number_of_people, group_size, affinity):
        return Instance(n=number_of_people, m=group_size, a=affinity)

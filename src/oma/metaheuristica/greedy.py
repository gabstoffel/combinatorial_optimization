import random

from oma.instance import Instance


def greedy_construction(
    instance: Instance, start_person: int | None = None
) -> list[int]:
    """Constrói um grupo inicial de forma gulosa: parte de uma pessoa e adiciona
    repetidamente quem traz o maior ganho de afinidade, até o grupo atingir o
    tamanho `m`.

    Usar uma pessoa inicial aleatória (o padrão) evita o viés de sempre começar
    pela pessoa 0.
    """
    num_people = instance.n
    group_size = instance.m
    affinity = instance.affinity  # matriz affinity[i][j] (não a lista de tuplas .a)

    # Sem pessoa inicial definida, sorteia uma para evitar viés.
    if start_person is None:
        start_person = random.randint(0, num_people - 1)

    group = {start_person}

    # affinity_gain[p] = ganho de afinidade ao adicionar a pessoa `p` ao grupo
    # atual. Começa com a afinidade de cada pessoa em relação à pessoa inicial.
    affinity_gain = [0.0] * num_people
    for person in range(num_people):
        if person not in group:
            affinity_gain[person] += affinity[start_person][person]

    while len(group) < group_size:
        # Escolhe, entre quem está de fora, a pessoa que mais aumenta a
        # afinidade total do grupo (maior ganho acumulado).
        best_person = max(
            (person for person in range(num_people) if person not in group),
            key=lambda person: affinity_gain[person],
        )
        group.add(best_person)

        # Atualiza incrementalmente os ganhos: agora cada pessoa de fora também
        # ganha a afinidade em relação ao membro recém-adicionado.
        for person in range(num_people):
            if person not in group:
                affinity_gain[person] += affinity[best_person][person]

    return list(group)


def random_construction(instance: Instance) -> list[int]:
    """Constrói um grupo inicial escolhendo `m` pessoas distintas de forma
    uniformemente aleatória.

    Serve como linha de base sem viés para comparar com a construção gulosa.
    """
    return random.sample(range(instance.n), instance.m)

from pulp import LpMaximize, LpProblem, LpVariable, lpSum

from oma.instance import Instance


def build_model(instance: Instance) -> LpProblem:
    problem = LpProblem("OMA", LpMaximize)

    # cria variáveis binárias {x1, x2, ... xn}
    # cada variável xi representa se a pessoa i está no grupo ou não
    selected = {
        person: LpVariable(f"x_{person}", cat="Binary")
        for person in range(instance.n)
    }

    # cria uma variável de decisão zij para cada aresta em a (matriz de afinidade)
    paired = {
        (i, j): LpVariable(f"z_{i}_{j}", cat="Binary") for i, j, _ in instance.a
    }

    # função objetivo: soma aij * zij
    problem += lpSum(affinity * paired[i, j] for i, j, affinity in instance.a)

    # restrições:
    # 1. o número de pessoas selecionadas deve ser igual a m (tamanho do grupo)
    problem += lpSum(selected.values()) == instance.m

    # 2. e 3. ligam zij aos extremos: o par só conta se ambos forem selecionados
    for i, j, _ in instance.a:
        problem += paired[i, j] <= selected[i]
        problem += paired[i, j] <= selected[j]
        problem += paired[i, j] >= selected[i] + selected[j] - 1

    return problem

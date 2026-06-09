from pulp import LpMaximize, LpProblem
from pulp import lpSum, LpVariable

from oma.instance import Instance


def build_model(instance: Instance) -> LpProblem:
    prob = LpProblem("OMA", LpMaximize)
   
    #cria variáveis binárias {x1, x2, x3, ... xn} 
    #cada variavel xi aqui representa se a pessoa i está no grupo ou não
    x = {i: LpVariable(f"x_{i}", cat="Binary") for i in range(instance.n)}
    
    
    #criamos uma variavel de decisão zij para cada aresta em a (matriz de afinidade)
    z = {}
    for i, j, aij in instance.a:
        z[i, j] = LpVariable(f"z_{i}_{j}", cat="Binary")
        
    #representa a função objetivo
    # sum aij * zij
    prob += lpSum(aij * z[i, j] for i, j, aij in instance.a)
   
    # restrições:
    
    # 1. o número de pessoas selecionadas deve ser igual a m (tamanho do grupo)
    prob += lpSum(x[i] for i in range(instance.n)) == instance.m
    
    # 2. 
    for i, j, _ in instance.a:
        prob += z[i, j] <= x[i]
        prob += z[i, j] <= x[j]
    
    # 3. 
    for i, j, _ in instance.a:
        prob += z[i, j] >= x[i] + x[j] - 1

   
    return prob

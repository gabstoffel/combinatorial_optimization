import pulp
import time
import os

def ler_instancia_oma(caminho_arquivo):
    """
    Lê o arquivo .dat, extrai n, p e cria um dicionário com os pesos das arestas.
    """
    pesos = {}
    with open(caminho_arquivo, 'r') as f:
        linhas = f.readlines()
        
        # Primeira linha: n (total de elementos) e p (tamanho do subconjunto)
        cabecalho = linhas[0].strip().split()
        n = int(cabecalho[0])
        p = int(cabecalho[1])
        
        # Restante das linhas: arestas no formato "i j peso"
        for linha in linhas[1:]:
            dados = linha.strip().split()
            if len(dados) >= 3:
                i = int(dados[0])
                j = int(dados[1])
                w = float(dados[2])
                pesos[(i, j)] = w
                
    return n, p, pesos

def resolver_oma_definitivo(n, p, pesos, caminho_cplex=None, limite_tempo=300):
    """
    Monta o modelo de Programação Linear Inteira e resolve usando o CPLEX Studio completo.
    """
    # 1. Instancia o problema de maximização
    prob = pulp.LpProblem("OMA_Programacao_Inteira", pulp.LpMaximize)
    
    # 2. Variáveis de Decisão (Binárias)
    print("Declarando variáveis...")
    x = pulp.LpVariable.dicts("x", range(n), cat=pulp.LpBinary)
    y = pulp.LpVariable.dicts("y", pesos.keys(), cat=pulp.LpBinary)
    
    # 3. Função Objetivo
    print("Montando função objetivo e restrições...")
    prob += pulp.lpSum(w * y[i, j] for (i, j), w in pesos.items()), "Total_Diversidade"
    
    # 4. Restrição de Cardinalidade (exatamente 'p' elementos)
    prob += pulp.lpSum(x[i] for i in range(n)) == p, "Definicao_Tamanho_p"
    
    # 5. Restrições de Vinculação Lógica
    for (i, j) in pesos.keys():
        prob += y[i, j] <= x[i], f"Vnculo_No_I_{i}_{j}"
        prob += y[i, j] <= x[j], f"Vnculo_No_J_{i}_{j}"
        # A restrição abaixo garante a lógica estrita da PLI:
        prob += y[i, j] >= x[i] + x[j] - 1, f"Ativacao_Aresta_{i}_{j}"
        
    # 6. Configuração do Solver CPLEX (Versão Completa via CMD)
    # Se o caminho for fornecido, usa ele. Se não, confia no PATH do Windows.
    if caminho_cplex and os.path.exists(caminho_cplex):
        solver = pulp.CPLEX_CMD(path=caminho_cplex, msg=True, timeLimit=limite_tempo)
    else:
        solver = pulp.CPLEX_CMD(msg=True, timeLimit=limite_tempo)
    
    print(f"\nIniciando o motor CPLEX para n={n}, p={p} (Limite de Tempo: {limite_tempo}s)...")
    tempo_inicio = time.time()
    
    # Resolve o modelo
    status = prob.solve(solver)
    
    tempo_execucao = time.time() - tempo_inicio
    
    # 7. Coleta de Resultados
    status_solucao = pulp.LpStatus[status]
    valor_objetivo = pulp.value(prob.objective)
    
    return valor_objetivo, tempo_execucao, status_solucao, x

# =====================================================================
# BLOCO PRINCIPAL
# =====================================================================
if __name__ == "__main__":
    
    # 1. Caminho da sua instância (ajustado conforme seu log anterior)
    caminho_instancia = r"dataset/oma02.dat" 
    
    # 2. CAMINHO DO EXECUTÁVEL DO CPLEX (MUITO IMPORTANTE)
    # Vá em "C:\Program Files\IBM\ILOG\..." até achar a pasta "bin\x64_win64\cplex.exe"
    # Substitua o caminho abaixo pelo caminho real da sua máquina:
    CAMINHO_CPLEX = r"C:\Program Files\IBM\ILOG\CPLEX_Studio222\cplex\bin\x64_win64\cplex.exe"
    
    # Define o tempo máximo que o CPLEX pode rodar (em segundos)
    # 600 segundos = 10 minutos (bom para instâncias difíceis)
    TEMPO_MAXIMO = 600
    
    try:
        print(f"Lendo o arquivo: {caminho_instancia}")
        n, p, pesos = ler_instancia_oma(caminho_instancia)
        
        fo, tempo, status_solucao, var_x = resolver_oma_definitivo(
            n, p, pesos, 
            caminho_cplex=CAMINHO_CPLEX, 
            limite_tempo=TEMPO_MAXIMO
        )
        
        print("\n" + "="*50)
        print("RESULTADOS FINAIS - BASELINE CPLEX")
        print("="*50)
        print(f"Status da Solução..: {status_solucao}")
        print(f"Função Objetivo....: {fo}")
        print(f"Tempo de Execução..: {tempo:.2f} segundos")
        
        # Recupera os nós selecionados
        elementos_escolhidos = [i for i in range(n) if var_x[i].varValue and var_x[i].varValue > 0.5]
        print(f"Nós Selecionados ({len(elementos_escolhidos)}): {elementos_escolhidos}")
        print("="*50)
        
    except FileNotFoundError:
        print(f"ERRO: O arquivo {caminho_instancia} não foi encontrado. Verifique o caminho.")
    except Exception as e:
        print(f"Ocorreu um erro durante a execução: {e}")
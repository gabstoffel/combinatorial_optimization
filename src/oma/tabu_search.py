from oma.instance import Instance

def calculate_objective(solution: set[int], affinity: list[list[float]]) -> float:
    """Helper function to calculate the total affinity of a given solution."""
    total = 0.0
    sol_list = list(solution)
    for i in range(len(sol_list)):
        for j in range(i + 1, len(sol_list)):
            total += affinity[sol_list[i]][sol_list[j]]
    return total

def run_tabu_search(
    instance: Instance, 
    initial_solution: list[int], 
    max_iter: int = 1000, 
    max_no_improve: int = 100, 
    tenure: int = 10
) -> tuple[list[int], float]:
    """
    Executes the Tabu Search algorithm to maximize the group's affinity.
    """
    n = instance.n
    affinity = instance.affinity
    
    current_solution = set(initial_solution)
    best_solution = set(initial_solution)
    
    current_obj = calculate_objective(current_solution, affinity)
    best_obj = current_obj
    
    tabu_list = {}
    
    iter_count = 0
    iters_without_improvement = 0
    all_people = set(range(n))
    
    while iter_count < max_iter and iters_without_improvement < max_no_improve:
        iter_count += 1
        
        best_delta = -float('inf')
        best_move = None  
        
        people_in = current_solution
        people_out = all_people - current_solution
        
        for p_out in people_in:
            for p_in in people_out:
                
                is_tabu = tabu_list.get(p_in, 0) >= iter_count
                
                delta = 0.0
                for i in people_in:
                    if i != p_out:
                        delta -= affinity[p_out][i]
                        delta += affinity[p_in][i]
                        
                if is_tabu and (current_obj + delta <= best_obj):
                    continue
                    
                if delta > best_delta:
                    best_delta = delta
                    best_move = (p_out, p_in)
                    
        if best_move:
            p_out, p_in = best_move
            
            current_solution.remove(p_out)
            current_solution.add(p_in)
            current_obj += best_delta
            
            tabu_list[p_out] = iter_count + tenure
            
            if (current_obj - best_obj) > 0.0001: 
                best_solution = set(current_solution)
                best_obj = current_obj
                iters_without_improvement = 0
            else:
                iters_without_improvement += 1
        else:

            break
            
    return list(best_solution), best_obj
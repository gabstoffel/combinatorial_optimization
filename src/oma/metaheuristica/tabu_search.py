import random

from oma.instance import Instance


def calculate_objective(group: set[int], affinity: list[list[float]]) -> float:
    """Soma das afinidades entre todos os pares de membros de `group`."""
    members = list(group)
    total = 0.0
    # Percorre cada par (i, j) sem repetição para somar a afinidade do par.
    for i in range(len(members)):
        for j in range(i + 1, len(members)):
            total += affinity[members[i]][members[j]]
    return total


def _swap_delta(
    leaving: int, entering: int, group: set[int], affinity: list[list[float]]
) -> float:
    """Variação do objetivo ao substituir `leaving` por `entering` em `group`.

    Calcula só a diferença (não o objetivo inteiro): para cada membro que
    permanece, soma a afinidade ganha com `entering` e desconta a perdida com
    `leaving`.
    """
    delta = 0.0
    for member in group:
        if member != leaving:
            delta += affinity[entering][member] - affinity[leaving][member]
    return delta


def _random_perturbation(
    group: set[int], everyone: set[int], affinity: list[list[float]]
) -> tuple[set[int], float]:
    """Troca um membro aleatório por alguém de fora também aleatório, devolvendo
    o novo grupo e seu objetivo. Usada para escapar de ótimos locais."""
    leaving = random.choice(list(group))
    entering = random.choice(list(everyone - group))
    new_group = (group - {leaving}) | {entering}
    return new_group, calculate_objective(new_group, affinity)


def run_tabu_search(
    instance: Instance,
    initial_solution: list[int],
    max_iter: int = 1000,
    max_no_improve: int = 100,
    tenure: int = 10,
    diversify_freq: int = 50,
) -> tuple[list[int], float]:
    """Maximiza a afinidade do grupo usando busca tabu.

    A cada iteração, troca o par (membro/pessoa de fora) com o maior ganho de
    objetivo, proibindo quem foi removido recentemente de voltar ao grupo por
    `tenure` iterações. A cada `diversify_freq` iterações o grupo sofre uma
    perturbação aleatória para escapar de ótimos locais. Para após `max_iter`
    iterações ou `max_no_improve` movimentos consecutivos sem melhora.
    """
    num_people = instance.n
    affinity = instance.affinity  # matriz affinity[i][j] (não a lista de tuplas .a)
    everyone = set(range(num_people))

    current_group = set(initial_solution)
    best_group = set(current_group)
    current_obj = calculate_objective(current_group, affinity)
    best_obj = current_obj

    # pessoa -> iteração até a qual ela não pode voltar a entrar no grupo (tabu).
    tabu_until: dict[int, int] = {}

    iteration = 0
    iters_without_improve = 0

    while iteration < max_iter and iters_without_improve < max_no_improve:
        iteration += 1

        # Diversificação periódica: a cada `diversify_freq` iterações, perturba
        # o grupo aleatoriamente e pula direto para a próxima iteração.
        if diversify_freq > 0 and iteration > 1 and iteration % diversify_freq == 0:
            current_group, current_obj = _random_perturbation(
                current_group, everyone, affinity
            )
            continue

        # Procura a melhor troca: maior delta entre todos os pares
        # (membro que sai, pessoa de fora que entra).
        best_delta = -float("inf")
        best_swap = None
        candidates_in = everyone - current_group

        for leaving in current_group:
            for entering in candidates_in:
                delta = _swap_delta(leaving, entering, current_group, affinity)

                # Respeita o tabu, exceto se o movimento superar o melhor já
                # encontrado (critério de aspiração).
                is_tabu = tabu_until.get(entering, 0) >= iteration
                if is_tabu and current_obj + delta <= best_obj:
                    continue

                if delta > best_delta:
                    best_delta = delta
                    best_swap = (leaving, entering)

        if best_swap is not None:
            # Aplica a melhor troca encontrada e marca quem saiu como tabu.
            leaving, entering = best_swap
            current_group.remove(leaving)
            current_group.add(entering)
            current_obj += best_delta
            tabu_until[leaving] = iteration + tenure

            # Atualiza o melhor global só se houver melhora significativa.
            if current_obj - best_obj > 1e-4:
                best_group = set(current_group)
                best_obj = current_obj
                iters_without_improve = 0
            else:
                iters_without_improve += 1
        elif iteration < max_iter - 10:
            # Nenhum movimento admissível: perturba em vez de desistir.
            current_group, current_obj = _random_perturbation(
                current_group, everyone, affinity
            )
            iters_without_improve += 1
        else:
            break

    return list(best_group), best_obj

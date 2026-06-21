"""Melhores valores conhecidos (BKV) por instância — fonte: docs/bkv.md.

Referência de qualidade para o desvio percentual da metaheurística e do solver
(quando o solver não prova o ótimo).
"""

BKV: dict[int, int] = {
    1: 472,
    2: 474,
    3: 470,
    4: 470,
    5: 474,
    6: 719,
    7: 724,
    8: 732,
    9: 733,
    10: 721,
}


def bkv_for(instance: str) -> int:
    """BKV de uma instância no formato 'omaNN' (ex.: 'oma01' -> 472)."""
    return BKV[int(instance[3:])]

from typing import Iterable, List, Set, Tuple


Edge = Tuple[int, int]


def greedy_mis(nodes: Iterable[int], edges: Iterable[Edge]) -> List[int]:
    """Greedy maximal independent set."""
    blocked: Set[int] = set()
    edge_set = set(tuple(sorted(e)) for e in edges)
    out: List[int] = []
    for n in nodes:
        if n in blocked:
            continue
        out.append(n)
        for a, b in edge_set:
            if a == n:
                blocked.add(b)
            elif b == n:
                blocked.add(a)
    return out

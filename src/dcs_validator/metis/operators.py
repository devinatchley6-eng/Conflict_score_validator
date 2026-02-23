from dataclasses import dataclass
from typing import Callable, Dict


@dataclass
class OperatorResult:
    name: str
    score: float


def apply_operator(name: str, scoring_fn: Callable[[str], float]) -> OperatorResult:
    return OperatorResult(name=name, score=float(scoring_fn(name)))


def default_operator_set() -> Dict[str, float]:
    return {"abduction": 0.4, "deduction": 0.3, "induction": 0.3}

import random
from typing import Dict


class MetaBandit:
    """Simple epsilon-greedy selector over operator rewards."""

    def __init__(self, epsilon: float = 0.1):
        self.epsilon = epsilon
        self.rewards: Dict[str, float] = {}

    def select(self, operators: Dict[str, float]) -> str:
        if random.random() < self.epsilon:
            return random.choice(list(operators.keys()))
        if self.rewards:
            return max(self.rewards, key=self.rewards.get)
        return max(operators, key=operators.get)

    def update(self, operator: str, reward: float) -> None:
        old = self.rewards.get(operator, 0.0)
        self.rewards[operator] = 0.5 * old + 0.5 * reward

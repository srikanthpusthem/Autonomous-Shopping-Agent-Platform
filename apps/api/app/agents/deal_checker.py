from __future__ import annotations

from app.agents.types import DealScore
from app.schemas import ProductCandidate


class DealCheckerAgent:
    def score(self, candidate: ProductCandidate) -> DealScore:
        # TODO: integrate historical pricing once a compliant source is selected.
        adjusted_price = max(candidate.price, 1)
        value_score = round((candidate.rating * 20) / adjusted_price * 100, 4)
        return DealScore(value_score=value_score)

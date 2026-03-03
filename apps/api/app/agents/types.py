from __future__ import annotations

from pydantic import BaseModel, Field


class CriteriaWeights(BaseModel):
    price: float = 0.35
    rating: float = 0.3
    delivery: float = 0.2
    durability: float = 0.15


class ShoppingPlan(BaseModel):
    category: str
    constraints: dict[str, str | float | int | list[str]] = Field(default_factory=dict)
    search_queries: list[str]
    evaluation_weights: CriteriaWeights


class ReviewInsight(BaseModel):
    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)
    recurring_issues: list[str] = Field(default_factory=list)
    warning_flags: list[str] = Field(default_factory=list)


class DealScore(BaseModel):
    value_score: float


class RankedProduct(BaseModel):
    provider: str
    product_id: str
    title: str
    brand: str | None = None
    price: float
    rating: float
    review_count: int
    eta_days: int
    shipping_cost: float
    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)
    why_recommended: str
    tradeoffs: str
    confidence: float
    total_score: float

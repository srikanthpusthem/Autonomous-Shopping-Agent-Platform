from __future__ import annotations

from pydantic import BaseModel, Field


class ProductCandidate(BaseModel):
    provider: str
    product_id: str
    title: str
    brand: str | None = None
    price: float
    rating: float = Field(ge=0, le=5)
    review_count: int = Field(ge=0)
    currency: str = "USD"
    attributes: dict[str, str] = Field(default_factory=dict)


class ProductDetails(BaseModel):
    provider: str
    product_id: str
    title: str
    description: str
    specs: dict[str, str] = Field(default_factory=dict)


class Review(BaseModel):
    provider: str
    product_id: str
    title: str
    body: str
    rating: float = Field(ge=0, le=5)
    verified_purchase: bool = False


class DeliveryInfo(BaseModel):
    provider: str
    product_id: str
    eta_days: int = Field(ge=0)
    shipping_cost: float = Field(ge=0)
    method: str


class SearchFilters(BaseModel):
    budget_min: float | None = None
    budget_max: float | None = None
    preferred_brands: list[str] = Field(default_factory=list)
    avoid_brands: list[str] = Field(default_factory=list)

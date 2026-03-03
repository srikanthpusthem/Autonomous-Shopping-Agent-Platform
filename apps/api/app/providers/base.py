from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas import DeliveryInfo, ProductCandidate, ProductDetails, Review, SearchFilters


class MarketplaceAdapter(ABC):
    provider_name: str

    @abstractmethod
    async def search_products(self, query: str, filters: SearchFilters) -> list[ProductCandidate]:
        raise NotImplementedError

    @abstractmethod
    async def get_product_details(self, product_id: str) -> ProductDetails:
        raise NotImplementedError

    @abstractmethod
    async def get_reviews(self, product_id: str) -> list[Review]:
        raise NotImplementedError

    @abstractmethod
    async def get_delivery(self, product_id: str, zip_code: str | None = None) -> DeliveryInfo:
        raise NotImplementedError

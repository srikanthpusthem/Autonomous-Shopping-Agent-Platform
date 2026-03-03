from __future__ import annotations

import asyncio
import json
import random
from pathlib import Path

from app.providers.base import MarketplaceAdapter
from app.providers.exceptions import ProviderNotFoundError, ProviderTimeoutError
from app.schemas import DeliveryInfo, ProductCandidate, ProductDetails, Review, SearchFilters


class FixtureMarketplaceAdapter(MarketplaceAdapter):
    def __init__(
        self, provider_name: str, fixture_path: Path, timeout_seconds: float = 1.5
    ) -> None:
        self.provider_name = provider_name
        self.timeout_seconds = timeout_seconds
        self.fixture_path = fixture_path
        self._fixture = self._load_fixture()

    def _load_fixture(self) -> dict:
        if not self.fixture_path.exists():
            raise FileNotFoundError(f"Missing provider fixture: {self.fixture_path}")
        with self.fixture_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    async def _with_latency(self) -> None:
        await asyncio.sleep(random.uniform(0.15, 0.45))

    async def _with_timeout(self, action):
        try:
            return await asyncio.wait_for(action, timeout=self.timeout_seconds)
        except TimeoutError as exc:
            raise ProviderTimeoutError(f"Timeout from provider {self.provider_name}") from exc

    def _find_product_record(self, product_id: str) -> dict:
        for product in self._fixture["products"]:
            if product["product_id"] == product_id:
                return product
        raise ProviderNotFoundError(
            f"Product '{product_id}' not found for provider '{self.provider_name}'"
        )

    async def search_products(self, query: str, filters: SearchFilters) -> list[ProductCandidate]:
        async def _search() -> list[ProductCandidate]:
            await self._with_latency()
            normalized_query = query.lower().strip()
            matched: list[ProductCandidate] = []
            for item in self._fixture["products"]:
                searchable = f"{item['title']} {item.get('description', '')}".lower()
                if normalized_query and normalized_query not in searchable:
                    continue
                if filters.budget_min is not None and item["price"] < filters.budget_min:
                    continue
                if filters.budget_max is not None and item["price"] > filters.budget_max:
                    continue
                brand = (item.get("brand") or "").lower()
                preferred = [b.lower() for b in filters.preferred_brands]
                avoid = [b.lower() for b in filters.avoid_brands]
                if preferred and brand not in preferred:
                    continue
                if brand in avoid:
                    continue
                matched.append(ProductCandidate(**item))
            return matched

        return await self._with_timeout(_search())

    async def get_product_details(self, product_id: str) -> ProductDetails:
        async def _details() -> ProductDetails:
            await self._with_latency()
            record = self._find_product_record(product_id)
            details = self._fixture.get("details", {}).get(product_id)
            if not details:
                raise ProviderNotFoundError(
                    f"Details missing for product '{product_id}' ({self.provider_name})"
                )
            return ProductDetails(
                provider=self.provider_name,
                product_id=product_id,
                title=record["title"],
                description=details.get("description", ""),
                specs=details.get("specs", {}),
            )

        return await self._with_timeout(_details())

    async def get_reviews(self, product_id: str) -> list[Review]:
        async def _reviews() -> list[Review]:
            await self._with_latency()
            review_rows = self._fixture.get("reviews", {}).get(product_id)
            if review_rows is None:
                raise ProviderNotFoundError(
                    f"Reviews missing for product '{product_id}' ({self.provider_name})"
                )
            return [
                Review(provider=self.provider_name, product_id=product_id, **row)
                for row in review_rows
            ]

        return await self._with_timeout(_reviews())

    async def get_delivery(self, product_id: str, zip_code: str | None = None) -> DeliveryInfo:
        async def _delivery() -> DeliveryInfo:
            await self._with_latency()
            delivery = self._fixture.get("delivery", {}).get(product_id)
            if not delivery:
                raise ProviderNotFoundError(
                    f"Delivery missing for product '{product_id}' ({self.provider_name})"
                )
            return DeliveryInfo(provider=self.provider_name, product_id=product_id, **delivery)

        return await self._with_timeout(_delivery())

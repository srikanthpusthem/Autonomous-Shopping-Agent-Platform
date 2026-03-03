from pathlib import Path

from app.providers.fixture_adapter import FixtureMarketplaceAdapter


class MockAmazonAdapter(FixtureMarketplaceAdapter):
    def __init__(self, timeout_seconds: float = 1.5) -> None:
        fixture_path = Path(__file__).resolve().parents[2] / "data" / "amazon_products.json"
        super().__init__(provider_name="mock_amazon", fixture_path=fixture_path, timeout_seconds=timeout_seconds)

from app.agents.deal_checker import DealCheckerAgent
from app.agents.decision import DecisionAgent
from app.agents.review_analyzer import ReviewAnalyzerAgent
from app.schemas import DeliveryInfo, ProductCandidate, Review


def _row(product_id: str, price: float, rating: float, eta_days: int, title: str) -> dict:
    candidate = ProductCandidate(
        provider="mock",
        product_id=product_id,
        title=title,
        brand="BrandX",
        price=price,
        rating=rating,
        review_count=500,
        currency="USD",
        attributes={"category": "headphones"},
    )
    delivery = DeliveryInfo(
        provider="mock",
        product_id=product_id,
        eta_days=eta_days,
        shipping_cost=0,
        method="standard",
    )
    reviews = [
        Review(
            provider="mock",
            product_id=product_id,
            title="Good value",
            body="Comfortable and reliable",
            rating=4,
            verified_purchase=True,
        )
    ]

    analyzer = ReviewAnalyzerAgent()
    deal = DealCheckerAgent().score(candidate)
    return {
        "candidate": candidate,
        "delivery": delivery,
        "insight": analyzer.analyze(reviews, "headphones"),
        "deal": deal,
    }


def test_decision_agent_ranks_by_weighted_score() -> None:
    agent = DecisionAgent()
    rows = [
        _row("p1", price=120, rating=4.8, eta_days=1, title="Premium"),
        _row("p2", price=80, rating=4.4, eta_days=2, title="Value"),
        _row("p3", price=60, rating=4.0, eta_days=3, title="Budget"),
    ]

    ranked = agent.rank(rows, {"price": 0.35, "rating": 0.3, "delivery": 0.2, "durability": 0.15})

    assert len(ranked) == 3
    assert ranked[0].total_score >= ranked[1].total_score >= ranked[2].total_score
    assert all(item.confidence >= 0.35 for item in ranked)

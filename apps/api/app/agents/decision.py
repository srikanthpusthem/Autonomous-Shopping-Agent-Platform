from __future__ import annotations

from app.agents.types import RankedProduct


class DecisionAgent:
    def rank(
        self,
        rows: list[dict],
        weights: dict[str, float],
    ) -> list[RankedProduct]:
        ranked: list[RankedProduct] = []
        for row in rows:
            price_score = 1 / max(row["candidate"].price, 1)
            rating_score = row["candidate"].rating / 5
            delivery_score = 1 / max(row["delivery"].eta_days, 1)
            durability_penalty = 0.2 if "durability_warning" in row["insight"].warning_flags else 0.0
            durability_score = max(0.1, 1 - durability_penalty)
            value_score = min(1.0, row["deal"].value_score / 5)

            total_score = (
                weights.get("price", 0.35) * price_score * 20
                + weights.get("rating", 0.3) * rating_score
                + weights.get("delivery", 0.2) * delivery_score
                + weights.get("durability", 0.15) * durability_score
                + 0.1 * value_score
            )

            confidence = max(0.35, min(0.95, round(0.55 + (row["candidate"].review_count / 5000), 2)))
            ranked.append(
                RankedProduct(
                    provider=row["candidate"].provider,
                    product_id=row["candidate"].product_id,
                    title=row["candidate"].title,
                    brand=row["candidate"].brand,
                    price=row["candidate"].price,
                    rating=row["candidate"].rating,
                    review_count=row["candidate"].review_count,
                    eta_days=row["delivery"].eta_days,
                    shipping_cost=row["delivery"].shipping_cost,
                    pros=row["insight"].pros,
                    cons=row["insight"].cons,
                    why_recommended=(
                        f"Balanced pick for {row['candidate'].title} with strong rating and value score."
                    ),
                    tradeoffs=(
                        "May trade off long-term durability"
                        if "durability_warning" in row["insight"].warning_flags
                        else "No major risks surfaced in fixture reviews"
                    ),
                    confidence=confidence,
                    total_score=round(total_score, 4),
                )
            )

        ranked.sort(key=lambda item: item.total_score, reverse=True)
        return ranked[:3]

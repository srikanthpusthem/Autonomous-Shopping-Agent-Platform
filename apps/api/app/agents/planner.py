from __future__ import annotations

from app.agents.types import CriteriaWeights, ShoppingPlan
from app.models.profile import Profile


class PlannerAgent:
    def plan(self, user_query: str, profile: Profile, memory_notes: list[str]) -> ShoppingPlan:
        query = user_query.lower()
        category = "general"
        if "headphone" in query or "earbud" in query:
            category = "headphones"
        elif "shoe" in query or "sneaker" in query:
            category = "shoes"

        constraints: dict[str, str | float | int | list[str]] = {
            "budget_min": float(profile.budget_min) if profile.budget_min is not None else 0,
            "budget_max": float(profile.budget_max) if profile.budget_max is not None else 99999,
            "shipping_speed_preference": profile.shipping_speed_preference,
            "preferred_brands": profile.preferred_brands,
            "avoid_brands": profile.avoid_brands,
            "use_case_tags": profile.use_case_tags,
        }
        if memory_notes:
            constraints["memory_notes"] = memory_notes

        shipping_pref = (profile.shipping_speed_preference or "balanced").lower()
        if shipping_pref == "fastest":
            weights = CriteriaWeights(price=0.25, rating=0.3, delivery=0.3, durability=0.15)
        elif shipping_pref == "cheapest":
            weights = CriteriaWeights(price=0.5, rating=0.25, delivery=0.15, durability=0.1)
        else:
            weights = CriteriaWeights()

        search_queries = [
            f"{category} {tag}".strip() for tag in (profile.use_case_tags or ["balanced choice"])
        ]
        if user_query not in search_queries:
            search_queries.insert(0, user_query)

        return ShoppingPlan(
            category=category,
            constraints=constraints,
            search_queries=search_queries,
            evaluation_weights=weights,
        )

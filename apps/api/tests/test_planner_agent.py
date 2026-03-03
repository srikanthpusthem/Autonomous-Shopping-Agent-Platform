from dataclasses import dataclass

from app.agents.planner import PlannerAgent


@dataclass
class FakeProfile:
    budget_min: float | None
    budget_max: float | None
    preferred_brands: list[str]
    avoid_brands: list[str]
    shipping_speed_preference: str
    use_case_tags: list[str]


def test_planner_extracts_category_and_constraints() -> None:
    agent = PlannerAgent()
    profile = FakeProfile(
        budget_min=50,
        budget_max=150,
        preferred_brands=["PulseFit"],
        avoid_brands=["CheapCo"],
        shipping_speed_preference="fastest",
        use_case_tags=["gym", "travel"],
    )

    plan = agent.plan("Need workout headphones", profile, ["prioritize comfort"])

    assert plan.category == "headphones"
    assert plan.constraints["budget_max"] == 150
    assert plan.constraints["preferred_brands"] == ["PulseFit"]
    assert plan.constraints["memory_notes"] == ["prioritize comfort"]
    assert plan.evaluation_weights.delivery > plan.evaluation_weights.durability
    assert len(plan.search_queries) >= 2

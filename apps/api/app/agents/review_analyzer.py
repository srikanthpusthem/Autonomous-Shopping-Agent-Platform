from __future__ import annotations

from app.agents.types import ReviewInsight
from app.schemas import Review


class ReviewAnalyzerAgent:
    def analyze(self, reviews: list[Review], category: str) -> ReviewInsight:
        pros: list[str] = []
        cons: list[str] = []
        issues: dict[str, int] = {}
        flags: list[str] = []

        for review in reviews:
            text = f"{review.title} {review.body}".lower()
            if review.rating >= 4:
                pros.append(review.title)
            else:
                cons.append(review.title)
            for keyword in ["durability", "wore", "dropout", "stiff", "battery", "bulky", "unsafe"]:
                if keyword in text:
                    issues[keyword] = issues.get(keyword, 0) + 1

        recurring_issues = [item for item, count in issues.items() if count >= 1]
        if any(key in recurring_issues for key in ["durability", "wore", "stiff"]):
            flags.append("durability_warning")
        if category == "shoes" and "unsafe" in recurring_issues:
            flags.append("gym_safety_warning")

        return ReviewInsight(
            pros=pros[:3],
            cons=cons[:3],
            recurring_issues=recurring_issues,
            warning_flags=flags,
        )

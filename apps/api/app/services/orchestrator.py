from __future__ import annotations

import asyncio
import logging
from uuid import UUID

from sqlalchemy import select

from app.agents.deal_checker import DealCheckerAgent
from app.agents.decision import DecisionAgent
from app.agents.memory import MemoryAgent
from app.agents.planner import PlannerAgent
from app.agents.review_analyzer import ReviewAnalyzerAgent
from app.db.session import SessionLocal
from app.models.product_snapshot import ProductSnapshot
from app.models.profile import Profile
from app.models.run import Run
from app.models.user import User
from app.providers import MockAmazonAdapter, MockBestBuyAdapter
from app.schemas import SearchFilters
from app.services.event_stream import persist_and_publish_event

logger = logging.getLogger(__name__)


class ShoppingRunOrchestrator:
    def __init__(self) -> None:
        self.planner = PlannerAgent()
        self.memory = MemoryAgent()
        self.review_analyzer = ReviewAnalyzerAgent()
        self.deal_checker = DealCheckerAgent()
        self.decision = DecisionAgent()
        self.adapters = [MockAmazonAdapter(), MockBestBuyAdapter()]

    async def execute_run(self, run_id: UUID) -> None:
        db = SessionLocal()
        try:
            run = db.scalar(select(Run).where(Run.id == run_id))
            if not run:
                return
            user = db.scalar(select(User).where(User.id == run.user_id))
            profile = db.scalar(select(Profile).where(Profile.id == run.profile_id))
            if not user or not profile:
                run.status = "error"
                db.commit()
                return

            run.status = "planning"
            db.commit()
            await persist_and_publish_event(
                db,
                run_id,
                "started",
                "PlannerAgent",
                "Building shopping plan",
            )

            memory_notes = self.memory.fetch_preference_notes(db, user.id, profile.id)
            plan = self.planner.plan(run.user_query, profile, memory_notes)
            await persist_and_publish_event(
                db,
                run_id,
                "finished",
                "PlannerAgent",
                "Plan complete",
                payload=plan.model_dump(),
            )

            run.status = "searching"
            db.commit()
            await persist_and_publish_event(
                db,
                run_id,
                "started",
                "MarketplaceSearchAgents",
                "Searching providers in parallel",
            )

            search_filters = SearchFilters(
                budget_min=float(profile.budget_min) if profile.budget_min is not None else None,
                budget_max=float(profile.budget_max) if profile.budget_max is not None else None,
                preferred_brands=profile.preferred_brands,
                avoid_brands=profile.avoid_brands,
            )

            query = plan.search_queries[0] if plan.search_queries else run.user_query
            candidate_lists = await asyncio.gather(
                *[adapter.search_products(query, search_filters) for adapter in self.adapters],
                return_exceptions=True,
            )

            candidates = []
            for item in candidate_lists:
                if isinstance(item, Exception):
                    logger.exception("provider-search-error", extra={"run_id": str(run_id)})
                    continue
                candidates.extend(item)

            await persist_and_publish_event(
                db,
                run_id,
                "progress",
                "MarketplaceSearchAgents",
                f"Found {len(candidates)} product candidates",
                payload={"candidate_count": len(candidates)},
            )

            rows: list[dict] = []
            for candidate in candidates:
                details_task = next(
                    adapter.get_product_details(candidate.product_id)
                    for adapter in self.adapters
                    if adapter.provider_name == candidate.provider
                )
                reviews_task = next(
                    adapter.get_reviews(candidate.product_id)
                    for adapter in self.adapters
                    if adapter.provider_name == candidate.provider
                )
                delivery_task = next(
                    adapter.get_delivery(candidate.product_id)
                    for adapter in self.adapters
                    if adapter.provider_name == candidate.provider
                )
                details, reviews, delivery = await asyncio.gather(
                    details_task,
                    reviews_task,
                    delivery_task,
                )

                insight = self.review_analyzer.analyze(reviews, plan.category)
                deal = self.deal_checker.score(candidate)
                rows.append(
                    {
                        "candidate": candidate,
                        "details": details,
                        "reviews": reviews,
                        "delivery": delivery,
                        "insight": insight,
                        "deal": deal,
                    }
                )

                snapshot = ProductSnapshot(
                    run_id=run.id,
                    provider=candidate.provider,
                    external_product_id=candidate.product_id,
                    title=candidate.title,
                    brand=candidate.brand,
                    price=candidate.price,
                    rating=candidate.rating,
                    raw_payload={
                        "candidate": candidate.model_dump(),
                        "details": details.model_dump(),
                        "delivery": delivery.model_dump(),
                    },
                )
                db.add(snapshot)
                db.commit()

            run.status = "analyzing"
            db.commit()
            await persist_and_publish_event(
                db,
                run_id,
                "finished",
                "ReviewAnalyzerAgent",
                "Review analysis complete",
            )

            run.status = "ranking"
            db.commit()
            ranked = self.decision.rank(rows, plan.evaluation_weights.model_dump())

            run.final_output = {
                "plan": plan.model_dump(),
                "top_recommendations": [item.model_dump() for item in ranked],
            }
            run.status = "done"
            db.commit()
            await persist_and_publish_event(
                db,
                run_id,
                "finished",
                "DecisionAgent",
                "Ranking complete",
                payload={"top_count": len(ranked)},
            )
            await persist_and_publish_event(db, run_id, "finished", "Run", "Run completed")
        except Exception as exc:
            logger.exception("run-execution-failed", extra={"run_id": str(run_id)})
            run = db.scalar(select(Run).where(Run.id == run_id))
            if run:
                run.status = "error"
                db.commit()
                await persist_and_publish_event(
                    db,
                    run_id,
                    "error",
                    "Run",
                    f"Run failed: {exc}",
                )
        finally:
            db.close()


orchestrator = ShoppingRunOrchestrator()

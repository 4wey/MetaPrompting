"""Critic module."""

from __future__ import annotations

from app.config import config
from app.schemas import CriticResult, PlanResult
from app.utils import read_text_file


class Critic:
    """Reviews the plan and draft solution and can request a replan."""

    def __init__(self, llm_client) -> None:
        self.llm_client = llm_client
        self.prompt_template = read_text_file(config.PROMPTS_DIR / "critic_prompt.md")

    def review(self, task: str, plan: PlanResult, draft_solution: str) -> CriticResult:
        steps_text = "\n".join(f"- {step}" for step in plan.steps)
        criteria_text = "\n".join(f"- {item}" for item in plan.quality_criteria)
        prompt = (
            f"{self.prompt_template}\n\n"
            f"Task: {task}\n"
            f"Strategy: {plan.strategy}\n"
            "Plan Steps:\n"
            f"{steps_text}\n"
            "Quality Criteria:\n"
            f"{criteria_text}\n"
            f"Draft Solution:\n{draft_solution}\n"
        )
        raw_text = self.llm_client.generate(prompt)
        needs_replan = "REPLAN" in raw_text
        return CriticResult(
            is_valid=not needs_replan,
            feedback=raw_text.strip(),
            needs_replan=needs_replan,
            raw_text=raw_text,
        )

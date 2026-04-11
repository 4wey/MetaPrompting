"""Solver module."""

from __future__ import annotations

from app.config import config
from app.schemas import PlanResult, SolverResult
from app.utils import read_text_file


class Solver:
    """Follows the provided plan without choosing a new strategy."""

    def __init__(self, llm_client) -> None:
        self.llm_client = llm_client
        self.prompt_template = read_text_file(config.PROMPTS_DIR / "solver_prompt.md")

    def solve(self, task: str, plan: PlanResult) -> SolverResult:
        steps_text = "\n".join(f"- {step}" for step in plan.steps)
        prompt = (
            f"{self.prompt_template}\n\n"
            f"Task: {task}\n"
            f"Strategy: {plan.strategy}\n"
            "Plan Steps:\n"
            f"{steps_text}\n"
        )
        raw_text = self.llm_client.generate(prompt)
        draft_solution = self._extract_draft_solution(raw_text)
        return SolverResult(draft_solution=draft_solution, raw_text=raw_text)

    @staticmethod
    def _extract_draft_solution(raw_text: str) -> str:
        if "Draft Solution:" in raw_text:
            return raw_text.split("Draft Solution:", 1)[1].strip()
        return raw_text.strip()

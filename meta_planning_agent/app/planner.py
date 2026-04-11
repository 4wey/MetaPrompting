"""Planner module."""

from __future__ import annotations

from app.config import config
from app.schemas import PlanResult
from app.utils import read_text_file


class Planner:
    """Builds a simple plan from the task using the prompt template and LLM client."""

    def __init__(self, llm_client) -> None:
        self.llm_client = llm_client
        self.prompt_template = read_text_file(config.PROMPTS_DIR / "planner_prompt.md")

    def build_plan(self, task: str) -> PlanResult:
        prompt = f"{self.prompt_template}\n\nTask: {task}\n"
        raw_text = self.llm_client.generate(prompt)
        parsed = self._parse_plan(raw_text)
        parsed.raw_text = raw_text
        return parsed

    def _parse_plan(self, raw_text: str) -> PlanResult:
        sections = {
            "strategy": "",
            "steps": [],
            "quality_criteria": [],
            "replan_conditions": [],
        }
        current_section: str | None = None

        for line in raw_text.splitlines():
            stripped = line.strip()
            if stripped.startswith("Strategy:"):
                sections["strategy"] = stripped.split("Strategy:", 1)[1].strip()
                current_section = None
            elif stripped == "Steps:":
                current_section = "steps"
            elif stripped == "Quality Criteria:":
                current_section = "quality_criteria"
            elif stripped == "Replan Conditions:":
                current_section = "replan_conditions"
            elif stripped.startswith("- ") and current_section:
                sections[current_section].append(stripped[2:].strip())

        return PlanResult(
            strategy=sections["strategy"] or "Use a step-by-step strategy.",
            steps=sections["steps"] or ["Clarify the task.", "Solve step by step.", "Check the result."],
            quality_criteria=sections["quality_criteria"]
            or ["The answer addresses the task.", "The answer is coherent."],
            replan_conditions=sections["replan_conditions"]
            or ["The answer is incomplete.", "Key constraints are missing."],
            raw_text=raw_text,
        )

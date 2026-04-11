"""LLM access layer.

Later this module can be replaced with a real API client.
For the MVP we use a predictable local stub so the project runs offline.
"""

from __future__ import annotations


class LLMClient:
    """Very small deterministic stub for Planner, Solver and Critic roles."""

    def __init__(self, model_name: str = "stub-meta-planning-model") -> None:
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        prompt_lower = prompt.lower()

        if "critic" in prompt_lower:
            return self._critic_response(prompt)
        if "solver" in prompt_lower:
            return self._solver_response(prompt)
        return self._planner_response(prompt)

    def _planner_response(self, prompt: str) -> str:
        task_line = self._extract_task(prompt)
        return (
            "Strategy: Break the problem into a small sequence of explicit steps, "
            "keep constraints visible, and validate the result against the task.\n"
            "Steps:\n"
            f"- Clarify the objective and constraints in the task: {task_line}\n"
            "- Choose a step-by-step strategy instead of answering in one jump.\n"
            "- Solve each stage in order and keep intermediate reasoning aligned with the plan.\n"
            "- Check whether the final answer satisfies the original task and constraints.\n"
            "Quality Criteria:\n"
            "- The answer addresses the full task.\n"
            "- The reasoning is coherent and multi-step.\n"
            "- Important constraints are reflected in the solution.\n"
            "Replan Conditions:\n"
            "- The solution is incomplete.\n"
            "- Important constraints are missing.\n"
            "- The reasoning contradicts the plan.\n"
        )

    def _solver_response(self, prompt: str) -> str:
        task_line = self._extract_task(prompt)
        steps = self._extract_section_items(prompt, "Plan Steps:")
        numbered_steps = "\n".join(
            f"{index}. {step}" for index, step in enumerate(steps, start=1)
        ) or "1. Follow the provided plan carefully."
        return (
            "Draft Solution:\n"
            f"Task summary: {task_line}\n"
            "Planned execution:\n"
            f"{numbered_steps}\n"
            "Result:\n"
            "This draft follows the provided strategy, works through the task in stages, "
            "and ends with a concise answer that remains consistent with the stated constraints."
        )

    def _critic_response(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        if "incomplete" in prompt_lower or "missing" in prompt_lower:
            return (
                "Critic verdict: REPLAN\n"
                "Feedback: The current result appears incomplete or misses an important "
                "constraint from the task. A revised plan is recommended."
            )

        return (
            "Critic verdict: VALID\n"
            "Feedback: The draft solution follows the plan, covers the task at a basic MVP level, "
            "and does not require replanning."
        )

    @staticmethod
    def _extract_task(prompt: str) -> str:
        for line in prompt.splitlines():
            if line.startswith("Task:"):
                return line.split("Task:", 1)[1].strip()
        return "No task provided."

    @staticmethod
    def _extract_section_items(prompt: str, header: str) -> list[str]:
        lines = prompt.splitlines()
        items: list[str] = []
        in_section = False

        for line in lines:
            if line.strip() == header:
                in_section = True
                continue
            if in_section and line.endswith(":") and not line.startswith("- "):
                break
            if in_section and line.startswith("- "):
                items.append(line[2:].strip())

        return items

"""LLM access layer.

Supports:
- local deterministic stub for offline development;
- YandexGPT via Yandex Cloud Foundation Models REST API.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import requests

from app.config import config


class LLMError(RuntimeError):
    """Raised when an LLM provider cannot return a valid response."""


@dataclass
class GenerationOptions:
    temperature: float | None = None
    max_tokens: int | None = None


class LLMClient:
    """Unified client for stub and Yandex providers."""

    def __init__(self, model_name: str | None = None, provider: str | None = None) -> None:
        self.model_name = model_name or config.MODEL_NAME
        self.provider = (provider or config.LLM_PROVIDER).lower().strip()

    def generate(self, prompt: str, options: GenerationOptions | None = None) -> str:
        if self.provider == "yandex":
            return self._generate_yandex(prompt, options or GenerationOptions())
        return self._generate_stub(prompt)

    def _generate_yandex(self, prompt: str, options: GenerationOptions) -> str:
        if not config.YANDEX_API_KEY:
            raise LLMError(
                "Для провайдера yandex не задан YANDEX_API_KEY в .env"
            )
        if not config.YANDEX_MODEL_URI:
            raise LLMError(
                "Для провайдера yandex не задан YANDEX_FOLDER_ID или YANDEX_MODEL_URI в .env"
            )

        payload = {
            "modelUri": config.YANDEX_MODEL_URI,
            "completionOptions": {
                "stream": False,
                "temperature": options.temperature if options.temperature is not None else config.DEFAULT_TEMPERATURE,
                "maxTokens": str(options.max_tokens if options.max_tokens is not None else config.DEFAULT_MAX_TOKENS),
            },
            "messages": [
                {"role": "user", "text": prompt},
            ],
        }
        headers = {
            "Authorization": f"Api-Key {config.YANDEX_API_KEY}",
            "Content-Type": "application/json",
        }
        if config.YANDEX_FOLDER_ID:
            headers["x-folder-id"] = config.YANDEX_FOLDER_ID

        response = requests.post(
            config.YANDEX_API_URL,
            headers=headers,
            json=payload,
            timeout=config.REQUEST_TIMEOUT_SEC,
        )
        if response.status_code >= 400:
            raise LLMError(
                f"Yandex API вернул ошибку {response.status_code}: {response.text}"
            )

        data = response.json()
        text = self._extract_yandex_text(data)
        if not text:
            raise LLMError(
                "Yandex API вернул ответ без текста: " + json.dumps(data, ensure_ascii=False)
            )
        return text.strip()

    @staticmethod
    def _extract_yandex_text(data: dict[str, Any]) -> str:
        result = data.get("result", data)
        alternatives = result.get("alternatives") or []
        if alternatives:
            first = alternatives[0]
            if isinstance(first, dict):
                message = first.get("message")
                if isinstance(message, dict) and message.get("text"):
                    return str(message["text"])
                if first.get("text"):
                    return str(first["text"])
        if result.get("text"):
            return str(result["text"])
        return ""

    def _generate_stub(self, prompt: str) -> str:
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

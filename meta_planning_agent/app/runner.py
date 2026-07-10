"""Helpers for running the agent on one task, a dataset, or interactively."""

from __future__ import annotations

import csv
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from app.agent import Agent
from app.config import config
from app.schemas import AgentState, TaskRecord
from app.utils import safe_filename, save_json, timestamp_string


def run_single_task(task_id: str, task: str) -> AgentState:
    agent = Agent()
    return agent.run(task_id=task_id, task=task)


def run_dataset(tasks: Iterable[TaskRecord]) -> tuple[list[AgentState], Path]:
    results: list[AgentState] = []
    timestamp = timestamp_string()
    output_path = config.RESULTS_DIR / f"dataset_run_{timestamp}.csv"

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "task_id",
                "category",
                "difficulty",
                "task",
                "strategy",
                "steps",
                "draft_solution",
                "critic_feedback",
                "final_answer",
                "replan_count",
            ],
        )
        writer.writeheader()
        for record in tasks:
            state = run_single_task(task_id=record.id, task=record.task)
            results.append(state)
            writer.writerow(
                {
                    "task_id": record.id,
                    "category": record.category,
                    "difficulty": record.difficulty,
                    "task": record.task,
                    "strategy": state.plan.strategy if state.plan else "",
                    "steps": " | ".join(state.plan.steps) if state.plan else "",
                    "draft_solution": state.draft_solution,
                    "critic_feedback": state.critic_feedback,
                    "final_answer": state.final_answer,
                    "replan_count": state.replan_count,
                }
            )
    return results, output_path


def save_run_log(state: AgentState) -> Path:
    file_name = f"{timestamp_string()}_{safe_filename(state.task_id)}.json"
    output_path = config.LOGS_DIR / file_name
    save_json(output_path, asdict(state))
    return output_path


def load_tasks_from_csv(csv_path: Path | None = None) -> list[TaskRecord]:
    target_path = csv_path or config.TASKS_CSV_PATH
    tasks: list[TaskRecord] = []
    with target_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            tasks.append(
                TaskRecord(
                    id=row.get("id", ""),
                    category=row.get("category", ""),
                    task=row.get("task", ""),
                    difficulty=row.get("difficulty", ""),
                    why_metaplanning_relevant=row.get("why_metaplanning_relevant", ""),
                    notes=row.get("notes", ""),
                )
            )
    return tasks

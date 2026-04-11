"""Helpers for running the agent and saving run logs."""

from __future__ import annotations

import csv
from dataclasses import asdict
from pathlib import Path

from app.agent import Agent
from app.config import config
from app.schemas import AgentState, TaskRecord
from app.utils import safe_filename, save_json, timestamp_string


def run_single_task(task_id: str, task: str) -> AgentState:
    agent = Agent()
    return agent.run(task_id=task_id, task=task)


def save_run_log(state: AgentState) -> Path:
    file_name = f"{timestamp_string()}_{safe_filename(state.task_id)}.json"
    output_path = config.LOGS_DIR / file_name
    save_json(output_path, asdict(state))
    return output_path


def load_tasks_from_csv() -> list[TaskRecord]:
    tasks: list[TaskRecord] = []
    with config.TASKS_CSV_PATH.open("r", encoding="utf-8", newline="") as file:
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

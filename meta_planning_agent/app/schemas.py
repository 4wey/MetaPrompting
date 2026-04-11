"""Dataclass schemas used across the MVP."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TaskRecord:
    id: str
    category: str
    task: str
    difficulty: str
    why_metaplanning_relevant: str
    notes: str


@dataclass
class PlanResult:
    strategy: str
    steps: list[str]
    quality_criteria: list[str]
    replan_conditions: list[str]
    raw_text: str


@dataclass
class SolverResult:
    draft_solution: str
    raw_text: str


@dataclass
class CriticResult:
    is_valid: bool
    feedback: str
    needs_replan: bool
    raw_text: str


@dataclass
class AgentState:
    task_id: str
    task: str
    plan: Optional[PlanResult] = None
    draft_solution: str = ""
    critic_feedback: str = ""
    final_answer: str = ""
    needs_replan: bool = False
    replan_count: int = 0
    run_history: list[dict] = field(default_factory=list)

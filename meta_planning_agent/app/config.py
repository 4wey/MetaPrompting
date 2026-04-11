"""Simple project configuration."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    """Static configuration for the local MVP."""

    BASE_DIR: Path
    PROMPTS_DIR: Path
    DATA_DIR: Path
    LOGS_DIR: Path
    MODEL_NAME: str
    MAX_REPLANS: int
    TASKS_CSV_PATH: Path


BASE_DIR = Path(__file__).resolve().parent.parent

config = AppConfig(
    BASE_DIR=BASE_DIR,
    PROMPTS_DIR=BASE_DIR / "prompts",
    DATA_DIR=BASE_DIR / "data",
    LOGS_DIR=BASE_DIR / "logs",
    MODEL_NAME="stub-meta-planning-model",
    MAX_REPLANS=2,
    TASKS_CSV_PATH=BASE_DIR / "data" / "tasks.csv",
)

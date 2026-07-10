"""Project configuration with environment-based provider settings."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class AppConfig:
    """Static configuration for the local MVP and API-backed runs."""

    BASE_DIR: Path
    PROMPTS_DIR: Path
    DATA_DIR: Path
    LOGS_DIR: Path
    RESULTS_DIR: Path
    TASKS_CSV_PATH: Path
    LLM_PROVIDER: str
    MODEL_NAME: str
    MAX_REPLANS: int
    REQUEST_TIMEOUT_SEC: int
    YANDEX_API_KEY: str
    YANDEX_FOLDER_ID: str
    YANDEX_MODEL_URI: str
    YANDEX_API_URL: str
    DEFAULT_TEMPERATURE: float
    DEFAULT_MAX_TOKENS: int


BASE_DIR = Path(__file__).resolve().parent.parent
YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID", "").strip()
DEFAULT_MODEL_NAME = os.getenv("MODEL_NAME", "yandexgpt-lite/latest").strip()

config = AppConfig(
    BASE_DIR=BASE_DIR,
    PROMPTS_DIR=BASE_DIR / "prompts",
    DATA_DIR=BASE_DIR / "data",
    LOGS_DIR=BASE_DIR / "logs",
    RESULTS_DIR=BASE_DIR / "results",
    TASKS_CSV_PATH=BASE_DIR / "data" / "tasks.csv",
    LLM_PROVIDER=os.getenv("LLM_PROVIDER", "stub").strip().lower(),
    MODEL_NAME=DEFAULT_MODEL_NAME,
    MAX_REPLANS=int(os.getenv("MAX_REPLANS", "2")),
    REQUEST_TIMEOUT_SEC=int(os.getenv("REQUEST_TIMEOUT_SEC", "60")),
    YANDEX_API_KEY=os.getenv("YANDEX_API_KEY", "").strip(),
    YANDEX_FOLDER_ID=YANDEX_FOLDER_ID,
    YANDEX_MODEL_URI=os.getenv(
        "YANDEX_MODEL_URI",
        f"gpt://{YANDEX_FOLDER_ID}/{DEFAULT_MODEL_NAME}" if YANDEX_FOLDER_ID else "",
    ).strip(),
    YANDEX_API_URL=os.getenv(
        "YANDEX_API_URL",
        "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
    ).strip(),
    DEFAULT_TEMPERATURE=float(os.getenv("DEFAULT_TEMPERATURE", "0.3")),
    DEFAULT_MAX_TOKENS=int(os.getenv("DEFAULT_MAX_TOKENS", "1200")),
)

# Ensure runtime directories exist.
config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)

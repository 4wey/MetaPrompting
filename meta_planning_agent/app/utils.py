"""Small helpers for file IO and serialization."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


def read_text_file(path: Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def ensure_dir(path: Path) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def dataclass_to_dict(obj: Any) -> Any:
    if is_dataclass(obj):
        return asdict(obj)
    if isinstance(obj, list):
        return [dataclass_to_dict(item) for item in obj]
    if isinstance(obj, dict):
        return {key: dataclass_to_dict(value) for key, value in obj.items()}
    return obj


def save_json(path: Path, data: Any) -> None:
    target = Path(path)
    ensure_dir(target.parent)
    target.write_text(
        json.dumps(dataclass_to_dict(data), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def timestamp_string() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def safe_filename(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "_", text.strip())
    return cleaned.strip("_") or "run"

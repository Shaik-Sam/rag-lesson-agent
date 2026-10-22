import os
from dataclasses import dataclass
from pathlib import Path

from .data import ROOT


def load_env_file(path=None):
    env_path = Path(path) if path else ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


@dataclass
class Settings:
    topic: str = "Introduction to RAG (Retrieval-Augmented Generation)"
    max_retries: int = 2
    generate_model: str = "claude-sonnet-5-5"
    judge_model: str = "claude-sonnet-5-5"
    memory_path: Path = ROOT / "memory" / "store.json"
    output_root: Path = ROOT / "outputs"
    promote_threshold: int = 2
    api_key: str = ""

    @classmethod
    def from_env(cls):
        load_env_file()
        settings = cls()
        settings.generate_model = os.environ.get("LESSON_MODEL", settings.generate_model)
        settings.judge_model = os.environ.get("JUDGE_MODEL", settings.judge_model)
        settings.api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        memory_override = os.environ.get("LESSON_MEMORY_PATH")
        if memory_override:
            settings.memory_path = Path(memory_override)
        output_override = os.environ.get("LESSON_OUTPUT_DIR")
        if output_override:
            settings.output_root = Path(output_override)
        return settings

    def clamped_retries(self, value=None):
        chosen = self.max_retries if value is None else value
        return max(0, min(2, int(chosen)))

import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"


@lru_cache(maxsize=None)
def load_json(name):
    with open(DATA_DIR / name, "r", encoding="utf-8") as handle:
        return json.load(handle)


def read_text(relative):
    return (DATA_DIR / relative).read_text(encoding="utf-8")


def reference_facts():
    return load_json("reference_facts.json")


def lesson_spec():
    return load_json("lesson_spec.json")


def language_rules():
    return load_json("language_rules.json")

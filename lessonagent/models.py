from dataclasses import asdict, dataclass, field
from typing import List


@dataclass
class Checkpoint:
    id: str
    name: str
    dimension: str
    kind: str
    requirement: str
    fix_hint: str


@dataclass
class CheckResult:
    id: str
    passed: bool
    reason: str
    evidence: List[str] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)

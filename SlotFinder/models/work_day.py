from dataclasses import dataclass
@dataclass
class WorkDay:
    id: int
    date: str
    start: str
    end: str
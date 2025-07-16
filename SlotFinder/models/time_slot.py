from dataclasses import dataclass

@dataclass
class TimeSlot:
    id: int
    day_id: int
    start: str
    end: str
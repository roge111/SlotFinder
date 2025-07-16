from typing import List, Dict, Optional, Tuple

from models.work_day import WorkDay
from models.time_slot import TimeSlot

class Schedule:
    def __init__(self, days: List[WorkDay], time_slots: List[TimeSlot]):
        self.days = days
        self.time_slots = time_slots

    def find_day_by_date(self, date: str) -> Optional[WorkDay]:
        """Находит рабочий день по дате."""
        for day in self.days:
            if day.date == date:
                return day
        return None

    def get_busy_intervals_for_day(self, day_id: int) -> List[Tuple[str, str]]:
        """Возвращает список занятых интервалов для указанного дня."""
        return [
            (slot.start, slot.end)
            for slot in self.time_slots
            if slot.day_id == day_id
        ]
from typing import List, Dict, Optional, Tuple

from models.work_day import WorkDay
from service.time_convertor import TimeUtils
from models.schedule import Schedule



class FreeTimeFinder:
    def __init__(self, schedule: Schedule):
        self.schedule = schedule
        self.time_utils = TimeUtils()

    def find_free_intervals(
        self,
        busy_intervals: List[Tuple[str, str]],
        work_day: WorkDay,
        time_interval: str
    ) -> Tuple[List[Tuple[str, str]], bool, Optional[Tuple[str, str]]]:
        """
        Находит свободные интервалы времени.
        
        Возвращает:
        - Список всех свободных интервалов
        - Флаг, доступен ли указанный интервал
        - Первый доступный интервал, куда можно вставить указанное время
        """
        free_intervals = []
        available_interval = None
        time_sec = self.time_utils.time_to_seconds(time_interval)
        start_day_sec = self.time_utils.time_to_seconds(work_day.start)
        end_day_sec = self.time_utils.time_to_seconds(work_day.end)
        last_end = work_day.start
        last_end_sec = start_day_sec
        is_available = False

        for interval in busy_intervals:
            start, end = interval
            start_sec = self.time_utils.time_to_seconds(start)
            end_sec = self.time_utils.time_to_seconds(end)

            if start_sec > last_end_sec:
                duration = start_sec - last_end_sec
                if not is_available and self.time_utils.is_time_slot_available(time_sec, duration):
                    is_available = True
                    available_interval = (last_end, start)
                free_intervals.append((last_end, start))

            last_end = end
            last_end_sec = end_sec

        # Проверяем интервал после последнего занятого слота
        if end_day_sec > last_end_sec:
            duration = end_day_sec - last_end_sec
            if not is_available and self.time_utils.is_time_slot_available(time_sec, duration):
                is_available = True
                available_interval = (last_end, work_day.end)
            free_intervals.append((last_end, work_day.end))

        return free_intervals, is_available, available_interval

    def find_available_days_for_interval(self, time_interval: str) -> List[Tuple[Tuple[str, str], str]]:
        """Находит все дни, где доступен указанный интервал времени."""
        available_days = []
        
        for day in self.schedule.days:
            busy_intervals = self.schedule.get_busy_intervals_for_day(day.id)
            if not busy_intervals:
                available_days.append(((day.start, day.end), day.date))
                continue
                
            _, is_available, available_interval = self.find_free_intervals(
                busy_intervals, day, time_interval
            )
            
            if is_available:
                available_days.append((available_interval, day.date))
                
        return available_days
from typing import List, Dict, Optional, Tuple

from models.time_slot import TimeSlot
from models.work_day import WorkDay
from models.schedule import Schedule

from service.free_time_finder import FreeTimeFinder


class ScheduleManager:
    def __init__(self, schedule_data: Dict):
        days = [WorkDay(**day) for day in schedule_data["days"]]
        time_slots = [TimeSlot(**slot) for slot in schedule_data["timeslots"]]
        self.schedule = Schedule(days, time_slots)
        self.free_time_finder = FreeTimeFinder(self.schedule)

    def find_available_time(self, date: str, time_interval: str):
        """Основной метод для поиска доступного времени."""
        work_day = self.schedule.find_day_by_date(date)
        
        if not work_day:
            print(f"День с датой {date} не найден в расписании.")
            return

        busy_intervals = self.schedule.get_busy_intervals_for_day(work_day.id)
        
        if not busy_intervals:
            print(f"Свободные промежутки с {work_day.start} до {work_day.end}")
            return
        else:
            self._print_busy_intervals(busy_intervals)


        free_intervals, is_available, available_interval = self.free_time_finder.find_free_intervals(
            busy_intervals, work_day, time_interval
        )

    

        if is_available:
            print(f"Да, промежуток {time_interval} доступен в этот день "
                  f"с {available_interval[0]} до {available_interval[1]}.")
        else:
            print(f"Нет, промежуток {time_interval} не доступен в этот день. "
                  "Хотите узнать, когда доступен этот промежуток в другие дни?")
            
            agree = input("Введите y или n (y - да, n - нет): ")
            if agree.lower() == 'y':
                available_days = self.free_time_finder.find_available_days_for_interval(time_interval)
                if available_days:
                    print("Есть доступные промежутки в эти дни и время:")
                    for interval, day_date in available_days:
                        print(f"Дата: {day_date} Время: {interval[0]} - {interval[1]}")
                else:
                    print("Ни в один день нет свободного времени.")

        self._print_free_intervals(free_intervals)

    def _print_free_intervals(self, intervals: List[Tuple[str, str]]):
        """Выводит на печать свободные интервалы времени."""
        if not intervals:
            print("Нет свободных промежутков в эту дату")
            return

        message = "Свободные промежутки времени доступны: "
        message_parts = [f"с {start} до {end}" for start, end in intervals]
        message += ", ".join(message_parts) + "."
        print(message)

    def _print_busy_intervals(self, intervals: List[Tuple[str, str]]):
        """Выводит на печать свободные интервалы времени."""
        if not intervals:
            print("Нет свободных промежутков в эту дату")
            return

        message = "Занятые промежутки времени доступны: "
        message_parts = [f"с {start} до {end}" for start, end in intervals]
        message += ", ".join(message_parts) + "."
        print(message)

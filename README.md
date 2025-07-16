# SlotFinder

Проект для управления расписанием. Помогает найти свободные временные интервалы

# О проекте

Система позволяет:
- Загружать данные о рабочих днях и занятых временных интервалов из API
- Находить свободные промежутки времени в расписании
- Проверять доступность конкретных временных интервалов
- Получать информацию о доступных слотах

# 🏗️ Структура проекта

```
schedule_manager/
│
├── __init__.py              # Пустой файл для создания пакета
├── models/                  # Директория для классов данных
│   ├── __init__.py
│   ├── work_day.py          # Класс WorkDay
│   ├── time_slot.py         # Класс TimeSlot
│   └── schedule.py          # Класс Schedule
│
├── services/                # Директория для сервисных классов
│   ├── __init__.py
│   ├── time_converter.py    # Класс TimeUtils 
│   └── free_time_finder.py  # Класс FreeTimeFinder
│
├── managers/                # Директория для менеджеров
│   ├── __init__.py
│   └── schedule_manager.py  # Основной класс ScheduleManager
│
└── main.py                  # Точка входа в программу
```

# 🧩 Основные компоненты

### Models
---
Это модели данных
#### WorwDay
```
from dataclasses import dataclass
@dataclass
class WorkDay:
    id: int
    date: str
    start: str
    end: str
```

Переменные:
- `id` — это id дня;
- `date` — дата соответствующего дня;
- `start` и `end` — время начала и конца рабочего дня.

#### TimeSlot

```
from dataclasses import dataclass

@dataclass
class TimeSlot:
    id: int
    day_id: int
    start: str
    end: str
```

Переменные:
- `id` — это id слота или же заявки (можно назвать по-разному);
- `day_id` — это id даты, в которую стоит данный слот;
- `start` и `end` — время начала и конца слота соответственно.

#### Schedule

```
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
```

Данный класс содержит несколько функций:
- `find_day_by_date` — находит информацию для даты: `id`, `start`, `end`;
- `get_busy_intervals_for_day` — возвращает список занятых интервалов для указанного дня.

### service
---
Содержит сервисные классы с бизнес-логикой проекта. Здесь происходят основные вычисляния и преобразования данных. 

#### TimeUtils
```
class TimeUtils:
    @staticmethod
    def time_to_seconds(time: str) -> int:
        """Конвертирует время в формате 'HH:MM' в секунды."""
        hours, minutes = map(int, time.split(':'))
        return hours * 3600 + minutes * 60

    @staticmethod
    def is_time_slot_available(
        time_sec: int, 
        free_slot_sec: int
    ) -> bool:
        """Проверяет, помещается ли интервал в свободный слот."""
        return time_sec <= free_slot_sec

```

Располагается в файле `time_convertor.py` и решает две задачи: перевод время в формате `HH:MM` в секунды и проверяет, помещается ли конкретный интервал в слот времени.

Методы:
- `time_to_seconds` - конвертирует формат времени `HH:MM` в секунды
- `is_time_slot_avalibale` - проверяет, помещается ли заданный интервал в свободный слот


#### FreeTimeFinder
```
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
```

Класс занимается анализом расписания и поиском свободных слотов. С помощью методов класса можно найти свободные слоты, а также определить, можно ли вставить конкретный интервал в расписание дня, если да, то в какой интервал времени, иначе можно найти подходящий интервал в другие дни. 

Методы:
- `find_free_intervals` — находит свободные интервалы, возвращает: список всех свободных слотов, флаг, можно ли вставить заданный интервал в расписание, первый доступный интервал, куда можно вставить указанное время.
- `find_available_days_interval` — находит все дни, где доступен указанный интервал времени.
### managers
---

####ScheduleManager

```
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

```
Основной класс для управления расписанием и поиска занятых и свободных интервалов.

Координирует работу моделей данных и сервиса `FreeTimeFinder` для предоставления пользователю информации о доступных временных слотах.

Атрибуты:
  - `schedule` — объект класса `Schedule`
  - `free_time_finder` — объект класса `FreeTimeFinder`


1) `find_available_time`
    Основной метод поиска доступных временных интервалов.
    
    WorkFlow:
     1. Находит рабочий день по дате
     2. Получает занятые интервалы
     3. Анализирует свободные окна
     4. Предоставляет пользователю результаты
    
    Output:
      - Доступные и занятые интервалы
      - Возможность бронирования
      - Альтернативные варианты, если на указанную дату не забронировать слот

2) `_print_free_intervals` — приватный класс, который делает форматированный вывод свободных интервалов.
 
3) `_print_busy_intervals` — приватный класс, который делает форматированный вывод занятых интервалов.



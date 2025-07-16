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
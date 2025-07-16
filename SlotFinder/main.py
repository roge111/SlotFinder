import requests

from managers.schedule_manager import ScheduleManager

# Пример использования
if __name__ == "__main__":

    url = "https://ofc-test-01.tspb.su/test-task/"
    try:
        response = requests.get(url)

        response.raise_for_status()

        chart = response.json()
    except requests.exceptions.RequestException as e:
        print(f'Ошибка при загрузке данных: {e}')

    manager = ScheduleManager(chart)
    manager.find_available_time("2025-02-16", "01:00")
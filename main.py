from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime  # Импортируем модуль для работы с временем

# Укажите путь к драйверу Chrome
driver_path = "/opt/homebrew/bin/chromedriver"

# Настройка опций для Chrome
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")  # Включаем headless режим
chrome_options.add_argument("--disable-gpu")  # Отключаем GPU, рекомендуется для headless режима
chrome_options.add_argument("--window-size=1920,1080")  # Устанавливаем размер окна

# Создаем экземпляр драйвера с опциями
service = Service(driver_path)

# Повторяем запрос 10 раз
for i in range(100000):
    start_time = time.time()  # Засекаем время начала итерации
    print(f"Итерация {i + 1} начата в: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    driver = webdriver.Chrome(service=service, options=chrome_options)
    try:
        # Открываем сайт
        print(f"Запрос к сайту начат в: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        driver.get("https://www.flashscore.com.ua/tennis/")

        # Закрываем баннер с куками
        try:
            cookie_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            cookie_button.click()
            print("Cookie banner closed")
        except Exception:
            print("Cookie banner not found, continuing")

        # Ждем загрузки фильтров
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "filters__group"))
        )

        # Ищем кнопку "LIVE" и кликаем по ней
        live_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'filters__tab')]/div[text()='LIVE']"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", live_button)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", live_button)
        print("Clicked on LIVE tab")

        # Ждем загрузки матчей
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "event__match"))
        )

        # Получаем все матчи на странице
        matches = driver.find_elements(By.CLASS_NAME, "event__match")

        all_matches = []  # Список всех матчей

        for match in matches:
            try:
                # Получаем имена игроков
                players = match.find_elements(By.CLASS_NAME, "event__participant")
                if len(players) < 2:
                    continue
                player1 = players[0].text.strip()
                player2 = players[1].text.strip()

                # Получаем статус матча (сеты или завершен)
                stages = match.find_elements(By.CLASS_NAME, "event__stage--block")
                match_status = [stage.text.strip() for stage in stages]

                # Добавляем матч в список с его статусом
                all_matches.append(f"{player1} vs {player2} - Статус: {', '.join(match_status)}")

            except Exception as e:
                pass  # Пропускаем, если что-то пошло не так

        # Вывод списка всех матчей
        print(f"Итерация {i + 1}: Все матчи:")
        for match in all_matches:
            print(match)

        # Даем немного времени перед закрытием
        time.sleep(2)

    finally:
        driver.quit()

    end_time = time.time()  # Засекаем время окончания итерации
    iteration_time = end_time - start_time  # Вычисляем время выполнения итерации
    print(f"Итерация {i + 1} завершена в: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Итерация {i + 1} завершена за {iteration_time:.2f} секунд")
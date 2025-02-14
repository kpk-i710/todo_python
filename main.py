import os
import time
import platform
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Определяем путь к текущей директории (где находится main.py)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Определяем операционную систему
os_name = platform.system().lower()

# Формируем путь к chromedriver внутри папки "drivers" вашего проекта
if os_name == "linux":
    driver_path = os.path.join(current_dir, "drivers", "chromedriver_linux")
elif os_name == "darwin":  # macOS
    driver_path = os.path.join(current_dir, "drivers", "chromedriver")
else:
    raise Exception("Unsupported operating system")

# Проверяем, что файл существует
if not os.path.exists(driver_path):
    raise FileNotFoundError(f"ChromeDriver не найден по пути: {driver_path}")

# На macOS и Linux делаем драйвер исполняемым (если ещё не установлен этот флаг)
if os.name != "nt":
    os.chmod(driver_path, 0o755)

# Настройка опций для Chrome
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")  # Включаем headless режим
chrome_options.add_argument("--disable-gpu")  # Отключаем GPU
chrome_options.add_argument("--window-size=1920,1080")  # Устанавливаем размер окна

# Создаем экземпляр службы с указанным chromedriver
service = Service(driver_path)

# Повторяем запрос 10 раз (или нужное количество итераций)
for i in range(100000):
    start_time = time.time()
    print(f"Итерация {i + 1} начата в: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    driver = webdriver.Chrome(service=service, options=chrome_options)
    try:
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
        all_matches = []

        for match in matches:
            try:
                players = match.find_elements(By.CLASS_NAME, "event__participant")
                if len(players) < 2:
                    continue
                player1 = players[0].text.strip()
                player2 = players[1].text.strip()

                stages = match.find_elements(By.CLASS_NAME, "event__stage--block")
                match_status = [stage.text.strip() for stage in stages]
                all_matches.append(f"{player1} vs {player2} - Статус: {', '.join(match_status)}")
            except Exception:
                pass

        print(f"Итерация {i + 1}: Все матчи:")
        for match in all_matches:
            print(match)

        # Небольшая пауза перед закрытием браузера
        time.sleep(2)
    finally:
        driver.quit()

    end_time = time.time()
    iteration_time = end_time - start_time
    print(f"Итерация {i + 1} завершена в: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Итерация {i + 1} завершена за {iteration_time:.2f} секунд")
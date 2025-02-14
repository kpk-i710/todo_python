import os
import time
import platform
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fastapi import FastAPI
import threading

app = FastAPI()

# Определяем операционную систему
os_name = platform.system().lower()

# Пути к Chrome и ChromeDriver
if os_name == "darwin":  # macOS
    CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
elif os_name == "linux":  # Linux (Render)
    CHROME_PATH = "/opt/render/opt/google/chrome/google-chrome"
else:
    raise RuntimeError(f"ОС {os_name} не поддерживается!")

# Путь к chromedriver (один и тот же для всех систем)
CHROMEDRIVER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "drivers", "chromedriver_linux")

# Проверяем, что файлы существуют
if not os.path.exists(CHROME_PATH):
    raise FileNotFoundError(f"Google Chrome не найден по пути: {CHROME_PATH}")
if not os.path.exists(CHROMEDRIVER_PATH):
    raise FileNotFoundError(f"ChromeDriver не найден по пути: {CHROMEDRIVER_PATH}")

# Делаем ChromeDriver исполняемым (если требуется)
os.chmod(CHROMEDRIVER_PATH, 0o755)

# Настройка Chrome
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = CHROME_PATH  # Указываем путь к Chrome
chrome_options.add_argument("--headless")  # Без GUI
chrome_options.add_argument("--disable-gpu")  # Отключить GPU
chrome_options.add_argument("--no-sandbox")  # Для контейнеров (на Linux)
chrome_options.add_argument("--disable-dev-shm-usage")  # Для работы в ограниченной памяти
chrome_options.add_argument("--window-size=1920,1080")  # Размер окна
chrome_options.add_argument("--remote-debugging-port=9222")  # Отладка

# Создаем экземпляр службы с указанным chromedriver
service = Service(CHROMEDRIVER_PATH)

def run_selenium():
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

# Запускаем Selenium в отдельном потоке
selenium_thread = threading.Thread(target=run_selenium)
selenium_thread.daemon = True
selenium_thread.start()

@app.get("/")
def read_root():
    return {"message": "Selenium script is running in the background!"}

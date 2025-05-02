from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def obter_dados_plyers(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    jogadores_furia = []

    try:
        driver.get(url)
        time.sleep(5)
        player_elements = driver.find_elements(By.CLASS_NAME, 'font-bold')
        player_names = [element.text for element in player_elements if element.text.strip() != ""]

        start_collecting = False

        for element in player_names:
            text = element.strip().upper()
            if not text:
                continue

            if "ELENCO" in text:
                start_collecting = True
                continue

            if start_collecting:
                if "FURIA" in text:
                    break
                jogadores_furia.append(text)
    except Exception as e:
        return f"Ocorreu um erro: {str(e)}"
    finally:
        driver.quit()

    return jogadores_furia

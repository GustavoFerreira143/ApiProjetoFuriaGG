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

    # Inicializar o navegador
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    jogadores_furia = []  

    try:
        # Acessar o site
        driver.get(url)

        # Esperar carregar o site
        time.sleep(5) 

        # Buscar os elementos com o nome dos jogadores
        player_elements = driver.find_elements(By.CLASS_NAME, 'font-bold')

        # Extrair os nomes
        player_names = [element.text for element in player_elements if element.text.strip() != ""]

        # Variável de controle
        start_collecting = False

        # Iterar sobre os elementos
        for element in player_names:
            text = element.strip().upper()  # Manipula a string para uppercase
            if not text:
                continue

            if "ELENCO" in text:  # Pesquisa se a string contém 'ELENCO'
                start_collecting = True
                continue

            if start_collecting:
                if "FURIA" in text:  # Pesquisa por 'FURIA'
                    break
                jogadores_furia.append(text)
    except Exception as e:
        return (f"Ocorreu um erro")
    finally:
        driver.quit()
    return jogadores_furia
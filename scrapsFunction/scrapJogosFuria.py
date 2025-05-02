from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import os
from dotenv import load_dotenv

load_dotenv()

def coletaJogosKingsLeague():
    # Configurações do Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Opcional: roda o Chrome em segundo plano
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Inicializar o navegador
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        # Acessar o site
        url = os.getenv('TIMES_FURIA_KINGS_LEAGUE')
        driver.get(url)

        # Esperar carregar o site
        time.sleep(5)

        # Buscar listas de elementos
        horaJogo = driver.find_elements(By.CLASS_NAME, 'match-hour')
        dataJogo = driver.find_elements(By.CLASS_NAME, 'turn-date')
        nomeTime = driver.find_elements(By.CLASS_NAME, 'team-short-name')
        placarJogoCasa = driver.find_elements(By.XPATH, '//div[@class="home-team-result-wrapper"]/div/div')
        placarJogoFora = driver.find_elements(By.XPATH, '//div[@class="away-team-result-wrapper"]/div/div')

        # Extrair textos
        horaJogo = [element.text.strip() for element in horaJogo if element.text.strip()]
        dataJogo = [element.text.strip() for element in dataJogo if element.text.strip()]
        nomeTime = [element.text.strip() for element in nomeTime if element.text.strip()]
        placarJogoCasa = [element.text.strip() for element in placarJogoCasa if element.text.strip()]
        placarJogoFora = [element.text.strip() for element in placarJogoFora if element.text.strip()]

        # Garantir que não vá dar erro de índice
        total_jogos = min(len(dataJogo), len(horaJogo), len(nomeTime) // 2, len(placarJogoCasa), len(placarJogoFora))

        jogos = []  # Lista que vai armazenar todos os dicionários

        for i in range(total_jogos):
            jogo = {
                "data": dataJogo[i],
                "hora": horaJogo[i],
                "time_casa": nomeTime[i*2],
                "placar_casa": placarJogoCasa[i],
                "time_fora": nomeTime[i*2+1],
                "placar_fora": placarJogoFora[i]
            }
            jogos.append(jogo)

        return jogos

        jogos_json = json.dumps(jogos, indent=4, ensure_ascii=False)


    except Exception as e:
        return (f"Ocorreu um erro")

    finally:
        driver.quit()

def coletaEscalacao():

    chrome_options = Options()
    chrome_options.add_argument("--headless")  
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

   
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:

        url = os.getenv('TIMES_FURIA_KINGS_LEAGUE')
        driver.get(url)


        time.sleep(5)

  
        playerName = driver.find_elements(By.CLASS_NAME, 'player-name')
        escalacaoPlayer = driver.find_elements(By.CLASS_NAME, 'player-role')


        playerName = [element.text.strip() for element in playerName if element.text.strip()]
        escalacaoPlayer = [element.text.strip() for element in escalacaoPlayer if element.text.strip()]


        total_jogadores = min(len(playerName), len(escalacaoPlayer))

        jogos = []  

        for i in range(total_jogadores):
            jogo = {
                "nomeJogador": playerName[i],
                "Escalado": escalacaoPlayer[i],
            }
            jogos.append(jogo)

        return jogos

        jogos_json = json.dumps(jogos, indent=4, ensure_ascii=False)
        

    except Exception as e:
        return (f"Ocorreu um erro")

    finally:
        driver.quit()

def coletaAoVivo():

    chrome_options = Options()
    chrome_options.add_argument("--headless")  
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")


    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
  
        url = os.getenv('TIMES_FURIA_KINGS_LEAGUE')
        driver.get(url)

     
        time.sleep(5)

      
        aovivo = driver.find_elements(By.CLASS_NAME, 'is-live-box')

  
        aovivo = [element.text.strip() for element in aovivo if element.text.strip()]
        return aovivo

    except Exception as e:
        return (f"Ocorreu um erro")

    finally:
        driver.quit()
from playwright.sync_api import sync_playwright
import json
import os
from dotenv import load_dotenv

load_dotenv()
def coletaJogosKingsLeague():
    url = os.getenv('TIMES_FURIA_KINGS_LEAGUE')
    jogos = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)

            page.wait_for_timeout(5000)

            horaJogo = page.locator('.match-hour').all()
            dataJogo = page.locator('.turn-date').all()
            nomeTime = page.locator('.team-short-name').all()
            placarJogoCasa = page.locator('.home-team-result-wrapper div div').all()
            placarJogoFora = page.locator('.away-team-result-wrapper div div').all()

            # Extrair texto
            horaJogo = [el.inner_text().strip() for el in horaJogo if el.inner_text().strip()]
            dataJogo = [el.inner_text().strip() for el in dataJogo if el.inner_text().strip()]
            nomeTime = [el.inner_text().strip() for el in nomeTime if el.inner_text().strip()]
            placarJogoCasa = [el.inner_text().strip() for el in placarJogoCasa if el.inner_text().strip()]
            placarJogoFora = [el.inner_text().strip() for el in placarJogoFora if el.inner_text().strip()]

            total_jogos = min(len(dataJogo), len(horaJogo), len(nomeTime) // 2, len(placarJogoCasa), len(placarJogoFora))

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

            browser.close()
            return jogos

    except Exception as e:
        return f"Ocorreu um erro: {str(e)}"

def coletaEscalacao():
    url = os.getenv('TIMES_FURIA_KINGS_LEAGUE')
    jogos = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)

            page.wait_for_timeout(5000)

            playerName = page.locator('.player-name').all()
            escalacaoPlayer = page.locator('.player-role').all()

            playerName = [el.inner_text().strip() for el in playerName if el.inner_text().strip()]
            escalacaoPlayer = [el.inner_text().strip() for el in escalacaoPlayer if el.inner_text().strip()]

            total_jogadores = min(len(playerName), len(escalacaoPlayer))

            for i in range(total_jogadores):
                jogo = {
                    "nomeJogador": playerName[i],
                    "Escalado": escalacaoPlayer[i],
                }
                jogos.append(jogo)

            browser.close()
            return jogos

    except Exception as e:
        return f"Ocorreu um erro: {str(e)}"


def coletaAoVivo():
    url = os.getenv('TIMES_FURIA_KINGS_LEAGUE')
    aovivo = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)

            page.wait_for_timeout(5000)

            aovivo_elements = page.locator('.is-live-box').all()

            aovivo = [el.inner_text().strip() for el in aovivo_elements if el.inner_text().strip()]

            browser.close()
            return aovivo

    except Exception as e:
        return f"Ocorreu um erro: {str(e)}"


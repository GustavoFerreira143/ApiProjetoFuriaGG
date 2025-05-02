from playwright.sync_api import sync_playwright

def obter_dados_plyers(url):
    jogadores_furia = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(5000)
        elements = page.locator(".font-bold").all()
        texts = [el.inner_text().strip() for el in elements if el.inner_text().strip()]
        start_collecting = False
        for text in texts:
            upper_text = text.upper()
            if "ELENCO" in upper_text:
                start_collecting = True
                continue
            if start_collecting:
                if "FURIA" in upper_text:
                    break
                jogadores_furia.append(upper_text)
        browser.close()
    return jogadores_furia
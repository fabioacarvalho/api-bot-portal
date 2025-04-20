from playwright.sync_api import sync_playwright
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import sys
from twocaptcha import TwoCaptcha
import json
from pathlib import Path
import base64



class AutomationService:

    def extrair_dados(self, html, screenshot:str = None, filename: str = None):
        print("Extraindo dados...")

        soup = BeautifulSoup(html, "html.parser")

        # Extrair da tabela
        tabela = soup.find("table", {"id": "tabela-visao-geral-sancoes"})
        dados_tabela = []

        if tabela:
            linhas = tabela.find("tbody").find_all("tr")
            for linha in linhas:
                colunas = linha.find_all("td")
                if len(colunas) >= 4:
                    nis = colunas[1].get_text(strip=True)
                    nome = colunas[2].get_text(strip=True)
                    valor = colunas[3].get_text(strip=True)
                    dados_tabela.append({
                        "nis": nis,
                        "nome": nome,
                        "valor_recebido": valor
                    })

        # Extrair CPF e Localidade
        dados_secao = soup.find("section", {"class": "dados-tabelados"})
        cpf = localidade = nome_completo = None

        if dados_secao:
            campos = dados_secao.find_all("div", class_="col-xs-12")
            for campo in campos:
                strong = campo.find("strong")
                span = campo.find("span")
                if strong and span:
                    titulo = strong.get_text(strip=True).lower()
                    valor = span.get_text(strip=True)
                    if "cpf" in titulo:
                        cpf = valor
                    elif "localidade" in titulo:
                        localidade = valor
                    elif "nome" in titulo:
                        nome_completo = valor

        _href = soup.find("a", {"id": "btnDetalharBpc"})
        # detalhes = self.scrape_table_from_href(_href.attrs["href"]) if _href else []

        date = datetime.now().strftime("%Y%m%d_%H%M%S")

        resultado = {
            "data_consulta": date,
            "cpf": cpf,
            "localidade": localidade,
            "nome_completo": nome_completo,
            "beneficios": dados_tabela,
            "screenshot": {
                "filename": filename,
                "base64_image": screenshot
            }
            # "detalhes": detalhes
        }

        # Salvar no JSON
        data_path = Path("../data")
        data_path.mkdir(parents=True, exist_ok=True)
        date = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(data_path / f"{nome_completo.replace(' ', '_')}_dados_extraidos_{date}.json", "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=4)
        
        return resultado


    def solve(self, url: str, sitekey, iv, cp_context):
        API_KEY = "XXXXXXXXXXXXXXX"  # Substitua pelo seu API_KEY da 2Captcha

        solver = TwoCaptcha(API_KEY)

        try:
            result = solver.amazon_waf(
                sitekey='0x1AAAAAAAAkg0s2VIOD34y5',
                iv=iv,
                context=cp_context,
                url=url
            )
        except Exception as e:
            sys.exit(e)

        else:
            sys.exit('solved: ' + str(result))


    def take_screenshot(self, page, filename="screenshot"):
        date = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("../data", exist_ok=True)

        _filename = f"{filename}_{date}.png"
        _filepath = f"../data/{_filename}"

        # Tira o screenshot
        page.screenshot(path=_filepath)

        # Lê a imagem e converte para base64
        with open(_filepath, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

        return dict(filename=_filename, screenshot=encoded_string)


    def handle_cookies(self, page):
        try:
            page.locator('#accept-all-btn').wait_for(timeout=5000)
            print("Aceitar cookies encontrado. Clicando...")
            page.click("#accept-all-btn")
        except TimeoutError:
            # Screenshot antes de tentar localizar o campo
            self.take_screenshot(page, "erro_timeout_cookies")
            pass


    def buscar_dados(self, input_value: str):
        with sync_playwright() as p:

            url = "https://portaldatransparencia.gov.br/pessoa-fisica/busca/lista?pagina=1&tamanhoPagina=10"
            
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
            page = context.new_page()

            page.goto(url, wait_until="networkidle")

            # Verifica se o botão "Aceitar todos" existe e está visível
            try:
                self.handle_cookies(page)
            except:
                pass
            
            print("Preenchendo o termo de busca...")

            # Preencher termo de busca
            page.locator('input#termo').wait_for(state="visible")
            page.fill('input#termo', input_value)

            # Marcar filtro "Beneficiário de Programa Social"
            page.click('#accordion1')
            checkbox = page.locator('#beneficiarioProgramaSocial')
            checkbox.scroll_into_view_if_needed()
            page.evaluate("document.querySelector('#beneficiarioProgramaSocial').click()")

            # Clicar no botão de buscar
            page.click('#btnConsultarPF')

            print("Aguardando os resultados...")

            # Esperar os resultados aparecerem
            page.wait_for_selector('a.link-busca-nome')

            try:
                self.handle_cookies(page)
            except:
                pass

            # Pegando o primeiro link
            primeiro_link = page.locator('a.link-busca-nome').first

            print("Clicando no primeiro link...")

            # Clicar e esperar os detalhes carregarem
            primeiro_link.click()
            page.wait_for_load_state('networkidle')

            print("Aguardando os detalhes...")

            try:
                self.handle_cookies(page)
            except:
                pass

            # Recebimento de Recursos
            page.click('#accordion1')
            
            # Screenshot
            _screenshot = self.take_screenshot(page, f"{input_value}_recebimento_recursos")


            # Devido aos captchas que podem aparecer, é necessário esperar um pouco mais de codigo para resolver e algumas opcões que sao pagas.
            # # Detalhes do BPC
            # page.click('#btnDetalharBpc')

            # try:
            #     self.handle_cookies(page)
            # except:
            #     pass

            # try:
            #     page.locator('#amzn-captcha-verify-button').wait_for(state="visible", timeout=5000)
            #     page.wait_for_selector('#amzn-btn-verify-internal')
            #     iv = page.get_attribute('input[name="iv"]', 'value')
            #     cp_context = page.get_attribute('input[name="context"]', 'value')
            #     sitekey = page.get_attribute('#captcha-box', 'data-sitekey')
            #     self.solve(page.url, sitekey, iv, cp_context)
            #     self.take_screenshot(page, f"{input_value}_captcha")
            # except:
            #     pass

            # page.wait_for_selector('.dados-detalhados')


            # Pegar o HTML da página
            html = page.content()

            browser.close()
            return dict(html=html, screenshot=_screenshot['screenshot'], filename=_screenshot['filename'])


    def scrape_table_from_href(self, href: str) -> list[dict]:
        url = f"https://portaldatransparencia.gov.br{href}?ordenarPor=mesFolha&direcao=desc"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                        '(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
        response = requests.get(url=url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        table = soup.find('table', {'id': 'tabelaDetalhe'})
        if not table:
            raise ValueError("Nenhuma tabela encontrada na página.")

        headers = [th.text.strip() for th in table.find_all('th')]
        if not headers:
            raise ValueError("A tabela não possui cabeçalhos (th).")

        data = []
        for row in table.find_all('tr')[1:]:  # Pula o cabeçalho
            cells = [td.text.strip() for td in row.find_all(['td', 'th'])]
            if len(cells) == len(headers):
                data.append(dict(zip(headers, cells)))
            else:
                continue

        return data

    def run(self, input_value: str):
        try:
            html = self.buscar_dados(input_value)
            dados = self.extrair_dados(html['html'], html['screenshot'], html['filename'])
            
            return {
                "status": "success",
                "message": "Automação realizada com sucesso.",
                "data": dados
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
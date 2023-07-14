import os
import requests
import zipfile
import tempfile
import shutil
import platform
import urllib.request
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException


def get_chromedriver_version():
    return '114.0.5735.90'  # Substitua pela versão mais recente do chromedriver disponível

def download_chromedriver():
    desired_location = 'driver'

    # Verificar se o chromedriver já existe no local desejado
    if os.path.isfile(os.path.join(desired_location, 'chromedriver.exe')):
        return os.path.join(desired_location, 'chromedriver.exe')

    # Verificar a arquitetura do sistema operacional
    if platform.architecture()[0] == '64bit':
        chromedriver_url = f'https://chromedriver.storage.googleapis.com/{get_chromedriver_version()}/chromedriver_win32.zip'
    else:
        chromedriver_url = f'https://chromedriver.storage.googleapis.com/{get_chromedriver_version()}/chromedriver_win32.zip'

    # Baixar o chromedriver e extrair o arquivo zip
    with tempfile.TemporaryDirectory() as temp_dir:
        download_path = os.path.join(temp_dir, 'chromedriver.zip')
        urllib.request.urlretrieve(chromedriver_url, download_path)
        with zipfile.ZipFile(download_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Mover o arquivo chromedriver para o local desejado
        final_path = os.path.join(temp_dir, 'chromedriver.exe')
        shutil.move(final_path, desired_location)

    return os.path.join(desired_location, 'chromedriver.exe')


def download_images(artist_name):
    chromedriver_path = download_chromedriver()
    
    service = webdriver.chrome.service.Service(chromedriver_path)

    options = webdriver.ChromeOptions()

    driver = webdriver.Chrome(service=service, options=options)

    wait = WebDriverWait(driver, 10, poll_frequency=0.1)

    # URL do Last.fm
    url = f'https://www.last.fm/music/{artist_name}/+images/'

    try:
        driver.get(url)

        while True:
            try:
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'col-main')))

                imagens = driver.find_elements(By.XPATH, '//div[@class="col-main"]//img')
                for imagem in imagens:
                    src = imagem.get_attribute('src')
                    response = requests.get(src)
                    if response.status_code == 200:
                        nome_arquivo = urlparse(src).path.split('/')[-1]
                        nome_arquivo = os.path.splitext(nome_arquivo)[0]
                        nome_arquivo = f"{nome_arquivo}.png"
                        caminho_arquivo = os.path.join(artist_name, nome_arquivo)
                        with open(caminho_arquivo, 'wb') as arquivo:
                            arquivo.write(response.content)

            except StaleElementReferenceException:
                print("Elemento ficou obsoleto. Localizando novamente.")
                imagens = driver.find_elements(By.XPATH, '//div[@class="col-main"]//img')
                for imagem in imagens:
                    src = imagem.get_attribute('src')
                    response = requests.get(src)
                    if response.status_code == 200:
                        nome_arquivo = urlparse(src).path.split('/')[-1]
                        nome_arquivo = os.path.splitext(nome_arquivo)[0]
                        nome_arquivo = f"{nome_arquivo}.png"
                        caminho_arquivo = os.path.join(artist_name, nome_arquivo)
                        with open(caminho_arquivo, 'wb') as arquivo:
                            arquivo.write(response.content)

            # Verificar se o botão "Next" está presente
            botao_next = driver.find_elements(By.XPATH, '//a[contains(text(),"Next")]')
            if len(botao_next) > 0:
                botao_next[0].click()
            else:
                print("Download Concluído")
                break

    except Exception as e:
        print(f"Ocorreu um erro: {str(e)}")

    finally:
        driver.quit()

artist_name = "Avril+Lavigne" # Coloque o nome do artista que deseja utilizando o + no lugar de espaço

os.makedirs(artist_name, exist_ok=True)

download_images(artist_name)

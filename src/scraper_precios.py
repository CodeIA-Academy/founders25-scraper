"""Scraper para la página de precios de codeia.dev"""

import logging
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

logger = logging.getLogger(__name__)


class PreciosScraper:
    """Scraper para extraer información de precios."""

    def __init__(self, url: str = "https://codeia.dev/precios"):
        """
        Inicializa el scraper de precios.

        Args:
            url: URL de la página de precios
        """
        self.url = url
        self.driver = None

    def setup_driver(self) -> webdriver.Chrome:
        """Configura y retorna el driver de Selenium."""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')

        # Ruta específica de Chrome en macOS
        chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

        try:
            # Intentar instalar chromedriver con webdriver-manager
            driver_path = ChromeDriverManager().install()
            logger.info(f"ChromeDriver instalado en: {driver_path}")

            # Verificar que el archivo sea ejecutable
            import os
            import stat
            if os.path.exists(driver_path):
                os.chmod(driver_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

            service = Service(driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            logger.warning(f"Error con ChromeDriverManager: {e}. Intentando con driver del sistema...")
            # Intentar sin especificar service
            driver = webdriver.Chrome(options=chrome_options)

        return driver

    def scrape(self) -> tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
        """
        Extrae los datos de precios de la página.

        Returns:
            Tupla con (datos_extraídos, errores)
        """
        precios_data = []
        errors = []

        try:
            logger.info(f"Iniciando scraping de precios: {self.url}")
            self.driver = self.setup_driver()
            self.driver.get(self.url)

            # Esperar a que la página cargue
            time.sleep(3)

            # Intentar encontrar elementos de precios
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Buscar cards de precios (ajustar selectores según la estructura real)
            pricing_cards = soup.find_all(['div', 'section'], class_=lambda x: x and any(
                term in str(x).lower() for term in ['price', 'pricing', 'plan', 'card']))

            if not pricing_cards:
                # Intento alternativo: buscar por estructura común
                pricing_cards = soup.find_all('div', class_=lambda x: x and 'card' in str(x).lower())

            logger.info(f"Elementos de precios encontrados: {len(pricing_cards)}")

            for idx, card in enumerate(pricing_cards, 1):
                try:
                    # Extraer nombre del plan
                    nombre_elem = card.find(['h1', 'h2', 'h3', 'h4'], class_=lambda x: x and any(
                        term in str(x).lower() for term in ['title', 'name', 'heading']))

                    if not nombre_elem:
                        nombre_elem = card.find(['h1', 'h2', 'h3', 'h4'])

                    nombre = nombre_elem.get_text(strip=True) if nombre_elem else f"Plan {idx}"

                    # Extraer precio
                    precio_elem = card.find(['span', 'div', 'p'], class_=lambda x: x and any(
                        term in str(x).lower() for term in ['price', 'cost', 'amount']))

                    if not precio_elem:
                        precio_elem = card.find(string=lambda text: text and ('$' in text or '€' in text or 'USD' in text))

                    precio = precio_elem.get_text(strip=True) if precio_elem else "No especificado"

                    # Extraer características
                    caracteristicas = []
                    features_list = card.find_all(['li', 'p'], class_=lambda x: x and 'feature' in str(x).lower())

                    if not features_list:
                        features_list = card.find_all('li')

                    for feature in features_list:
                        text = feature.get_text(strip=True)
                        if text and len(text) > 3:
                            caracteristicas.append(text)

                    precios_data.append({
                        'nombre': nombre,
                        'precio': precio,
                        'caracteristicas': caracteristicas,
                        'num_caracteristicas': len(caracteristicas)
                    })

                    logger.info(f"Plan extraído: {nombre}")

                except Exception as e:
                    error_msg = f"Error al procesar card de precio {idx}: {str(e)}"
                    logger.error(error_msg)
                    errors.append({
                        'tipo': 'precio_card',
                        'mensaje': error_msg,
                        'url': self.url
                    })

        except Exception as e:
            error_msg = f"Error al scrapear precios: {str(e)}"
            logger.error(error_msg)
            errors.append({
                'tipo': 'scraping_precios',
                'mensaje': error_msg,
                'url': self.url
            })

        finally:
            if self.driver:
                self.driver.quit()

        return precios_data, errors

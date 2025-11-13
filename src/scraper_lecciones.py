"""Scraper para la página de lecciones de codeia.dev"""

import logging
import re
from typing import List, Dict, Any
from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from src.utils import download_image

logger = logging.getLogger(__name__)


class LeccionesScraper:
    """Scraper para extraer información de lecciones."""

    def __init__(self, url: str = "https://codeia.dev/lecciones"):
        """
        Inicializa el scraper de lecciones.

        Args:
            url: URL de la página de lecciones
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

    def normalize_filename(self, text: str, max_length: int = 50) -> str:
        """
        Normaliza un texto para usarlo como nombre de archivo.

        Args:
            text: Texto a normalizar
            max_length: Longitud máxima del nombre

        Returns:
            Nombre de archivo normalizado
        """
        # Remover caracteres especiales
        text = re.sub(r'[^\w\s-]', '', text)
        # Reemplazar espacios por guiones
        text = re.sub(r'[\s_]+', '-', text)
        # Convertir a minúsculas
        text = text.lower().strip('-')
        # Limitar longitud
        return text[:max_length]

    def scrape(self, images_path: Path) -> tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
        """
        Extrae los datos de lecciones de la página.

        Args:
            images_path: Ruta donde guardar las imágenes

        Returns:
            Tupla con (datos_extraídos, errores)
        """
        lecciones_data = []
        errors = []

        try:
            logger.info(f"Iniciando scraping de lecciones: {self.url}")
            self.driver = self.setup_driver()
            self.driver.get(self.url)

            # Esperar a que la página cargue
            time.sleep(4)

            # Scroll para cargar contenido dinámico
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Buscar enlaces principales que contienen las lecciones (basado en el HTML proporcionado)
            leccion_items = soup.find_all('a', class_='block group', href=True)

            logger.info(f"Elementos de lecciones encontrados: {len(leccion_items)}")

            for idx, item in enumerate(leccion_items, 1):
                try:
                    # Extraer URL del video (desde el href del enlace principal)
                    href = item.get('href', '')
                    video_url = f"https://codeia.dev{href}" if href.startswith('/') else href

                    # Extraer título (h3 con font-semibold)
                    titulo_elem = item.find('h3', class_=lambda x: x and 'font-semibold' in str(x))
                    titulo = titulo_elem.get_text(strip=True) if titulo_elem else f"Lección {idx}"

                    # Extraer descripción (p con text-muted-foreground)
                    descripcion_elem = item.find('p', class_=lambda x: x and 'text-muted-foreground' in str(x) and 'line-clamp' in str(x))
                    descripcion = descripcion_elem.get_text(strip=True) if descripcion_elem else ""

                    # Extraer todas las etiquetas (badges)
                    etiquetas = []
                    badge_containers = item.find_all('div', class_=lambda x: x and 'inline-flex' in str(x) and 'rounded-full' in str(x))

                    for badge in badge_containers:
                        badge_text = badge.get_text(strip=True)
                        # Filtrar badges vacíos o con solo iconos
                        if badge_text and len(badge_text) > 1 and not badge_text.startswith('<?'):
                            etiquetas.append(badge_text)

                    # Extraer categoría (primer badge con estilo de color de fondo)
                    categoria = "General"
                    first_badge = item.find('div', class_=lambda x: x and 'inline-flex' in str(x) and 'rounded-full' in str(x))
                    if first_badge:
                        categoria = first_badge.get_text(strip=True)

                    # Extraer fecha (span con icono de calendario)
                    fecha = "No especificada"
                    fecha_container = item.find('svg', class_=lambda x: x and 'lucide-calendar' in str(x))
                    if fecha_container:
                        fecha_span = fecha_container.find_next('span')
                        if fecha_span:
                            fecha = fecha_span.get_text(strip=True)

                    # Extraer visualizaciones (span con icono de usuarios)
                    visualizaciones = "0"
                    users_icon = item.find('svg', class_=lambda x: x and 'lucide-users' in str(x))
                    if users_icon:
                        views_span = users_icon.find_next('span')
                        if views_span:
                            visualizaciones = views_span.get_text(strip=True)

                    # Extraer duración del video
                    duracion = ""
                    duracion_elem = item.find('div', class_=lambda x: x and 'absolute' in str(x) and 'bottom-2' in str(x))
                    if duracion_elem:
                        duracion = duracion_elem.get_text(strip=True)

                    # Extraer imagen de portada
                    imagen_url = ""
                    imagen_filename = ""
                    img_elem = item.find('img')

                    if img_elem:
                        imagen_url = img_elem.get('src', '') or img_elem.get('data-src', '')

                        if imagen_url:
                            # Descargar imagen
                            filename_base = self.normalize_filename(titulo)
                            download_result = download_image(imagen_url, images_path, filename_base)

                            if download_result['success']:
                                imagen_filename = download_result['filename']
                            else:
                                errors.append(download_result)

                    leccion = {
                        'titulo': titulo,
                        'descripcion': descripcion,
                        'etiquetas': etiquetas,
                        'fecha': fecha,
                        'visualizaciones': visualizaciones,
                        'categoria': categoria,
                        'duracion': duracion,
                        'imagen_portada': imagen_filename,
                        'imagen_url': imagen_url,
                        'url_video': video_url
                    }

                    lecciones_data.append(leccion)
                    logger.info(f"Lección extraída: {titulo}")

                except Exception as e:
                    error_msg = f"Error al procesar lección {idx}: {str(e)}"
                    logger.error(error_msg)
                    errors.append({
                        'tipo': 'leccion_item',
                        'mensaje': error_msg,
                        'url': self.url
                    })

        except Exception as e:
            error_msg = f"Error al scrapear lecciones: {str(e)}"
            logger.error(error_msg)
            errors.append({
                'tipo': 'scraping_lecciones',
                'mensaje': error_msg,
                'url': self.url
            })

        finally:
            if self.driver:
                self.driver.quit()

        return lecciones_data, errors

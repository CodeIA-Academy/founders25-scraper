"""Utilidades para el scraper."""

import os
import json
import csv
import requests
from pathlib import Path
from typing import List, Dict, Any
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


def create_output_directories(base_dir: str = "output") -> Dict[str, Path]:
    """
    Crea directorios para almacenar los resultados.

    Args:
        base_dir: Directorio base para los outputs

    Returns:
        Diccionario con las rutas creadas
    """
    paths = {
        'base': Path(base_dir),
        'images_precios': Path(base_dir) / 'images' / 'precios',
        'images_lecciones': Path(base_dir) / 'images' / 'lecciones',
        'data': Path(base_dir) / 'data'
    }

    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)

    return paths


def download_image(url: str, output_path: Path, filename: str) -> Dict[str, Any]:
    """
    Descarga una imagen desde una URL.

    Args:
        url: URL de la imagen
        output_path: Ruta donde guardar la imagen
        filename: Nombre del archivo

    Returns:
        Diccionario con el resultado de la descarga
    """
    try:
        response = requests.get(url, timeout=10, stream=True)
        response.raise_for_status()

        # Obtener extensión desde la URL o content-type
        ext = Path(urlparse(url).path).suffix
        if not ext:
            content_type = response.headers.get('content-type', '')
            if 'jpeg' in content_type or 'jpg' in content_type:
                ext = '.jpg'
            elif 'png' in content_type:
                ext = '.png'
            elif 'webp' in content_type:
                ext = '.webp'
            else:
                ext = '.jpg'

        filepath = output_path / f"{filename}{ext}"

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info(f"Imagen descargada: {filepath}")
        return {
            'success': True,
            'filepath': str(filepath),
            'filename': f"{filename}{ext}",
            'url': url
        }

    except Exception as e:
        logger.error(f"Error al descargar imagen {url}: {e}")
        return {
            'success': False,
            'error': str(e),
            'url': url
        }


def save_to_json(data: List[Dict], filepath: Path) -> None:
    """
    Guarda datos en formato JSON.

    Args:
        data: Datos a guardar
        filepath: Ruta del archivo
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info(f"JSON guardado: {filepath}")


def save_to_csv(data: List[Dict], filepath: Path) -> None:
    """
    Guarda datos en formato CSV.

    Args:
        data: Datos a guardar
        filepath: Ruta del archivo
    """
    if not data:
        logger.warning("No hay datos para guardar en CSV")
        return

    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    logger.info(f"CSV guardado: {filepath}")


def generate_report(precios_data: List[Dict], lecciones_data: List[Dict],
                   errors: List[Dict]) -> str:
    """
    Genera un informe del scraping.

    Args:
        precios_data: Datos de precios scrapeados
        lecciones_data: Datos de lecciones scrapeadas
        errors: Lista de errores encontrados

    Returns:
        String con el informe formateado
    """
    report = []
    report.append("=" * 60)
    report.append("INFORME DE SCRAPING - CODEIA.DEV")
    report.append("=" * 60)
    report.append("")

    # Resumen de precios
    report.append("--- PRECIOS ---")
    report.append(f"Total de planes extraídos: {len(precios_data)}")
    if precios_data:
        for i, plan in enumerate(precios_data, 1):
            report.append(f"\n  Plan {i}: {plan.get('nombre', 'N/A')}")
            report.append(f"  Precio: {plan.get('precio', 'N/A')}")
            caracteristicas = plan.get('caracteristicas', [])
            if isinstance(caracteristicas, list):
                report.append(f"  Características: {len(caracteristicas)}")
    report.append("")

    # Resumen de lecciones
    report.append("--- LECCIONES ---")
    report.append(f"Total de lecciones extraídas: {len(lecciones_data)}")
    if lecciones_data:
        categorias = {}
        for leccion in lecciones_data:
            cat = leccion.get('categoria', 'Sin categoría')
            categorias[cat] = categorias.get(cat, 0) + 1

        report.append("\nLecciones por categoría:")
        for cat, count in categorias.items():
            report.append(f"  - {cat}: {count}")

        report.append(f"\nPrimeras 5 lecciones:")
        for i, leccion in enumerate(lecciones_data[:5], 1):
            report.append(f"\n  {i}. {leccion.get('titulo', 'N/A')}")
            report.append(f"     Categoría: {leccion.get('categoria', 'N/A')}")
            report.append(f"     Visualizaciones: {leccion.get('visualizaciones', 'N/A')}")
    report.append("")

    # Errores
    report.append("--- ERRORES ---")
    if errors:
        report.append(f"Total de errores: {len(errors)}")
        for i, error in enumerate(errors, 1):
            report.append(f"\n  Error {i}:")
            report.append(f"  Tipo: {error.get('tipo', 'N/A')}")
            report.append(f"  Mensaje: {error.get('mensaje', 'N/A')}")
            if 'url' in error:
                report.append(f"  URL: {error.get('url', 'N/A')}")
    else:
        report.append("No se encontraron errores.")

    report.append("")
    report.append("=" * 60)

    return "\n".join(report)

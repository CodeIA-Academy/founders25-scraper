"""Script principal para ejecutar el scraper de CodeIA."""

import logging
import sys
from datetime import datetime
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent))

from src.scraper_precios import PreciosScraper
from src.scraper_lecciones import LeccionesScraper
from src.utils import (
    create_output_directories,
    save_to_json,
    save_to_csv,
    generate_report
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Función principal del scraper."""
    logger.info("=" * 60)
    logger.info("INICIANDO SCRAPER DE CODEIA.DEV")
    logger.info("=" * 60)

    # Crear directorios de salida
    paths = create_output_directories()
    logger.info(f"Directorios de salida creados en: {paths['base']}")

    # Almacenar todos los errores
    all_errors = []

    # --- SCRAPING DE PRECIOS ---
    logger.info("\n--- Scraping de Precios ---")
    precios_scraper = PreciosScraper()
    precios_data, precios_errors = precios_scraper.scrape()
    all_errors.extend(precios_errors)

    if precios_data:
        # Guardar precios en JSON
        save_to_json(precios_data, paths['data'] / 'precios.json')

        # Guardar precios en CSV
        # Convertir lista de características a string para CSV
        precios_csv = []
        for plan in precios_data:
            plan_csv = plan.copy()
            if isinstance(plan_csv.get('caracteristicas'), list):
                plan_csv['caracteristicas'] = ' | '.join(plan_csv['caracteristicas'])
            precios_csv.append(plan_csv)

        save_to_csv(precios_csv, paths['data'] / 'precios.csv')
        logger.info(f"✓ {len(precios_data)} planes de precios extraídos")
    else:
        logger.warning("⚠ No se extrajeron datos de precios")

    # --- SCRAPING DE LECCIONES ---
    logger.info("\n--- Scraping de Lecciones ---")
    lecciones_scraper = LeccionesScraper()
    lecciones_data, lecciones_errors = lecciones_scraper.scrape(paths['images_lecciones'])
    all_errors.extend(lecciones_errors)

    if lecciones_data:
        # Guardar lecciones en JSON
        save_to_json(lecciones_data, paths['data'] / 'lecciones.json')

        # Guardar lecciones en CSV
        # Convertir lista de etiquetas a string para CSV
        lecciones_csv = []
        for leccion in lecciones_data:
            leccion_csv = leccion.copy()
            if isinstance(leccion_csv.get('etiquetas'), list):
                leccion_csv['etiquetas'] = ', '.join(leccion_csv['etiquetas'])
            lecciones_csv.append(leccion_csv)

        save_to_csv(lecciones_csv, paths['data'] / 'lecciones.csv')
        logger.info(f"✓ {len(lecciones_data)} lecciones extraídas")
    else:
        logger.warning("⚠ No se extrajeron datos de lecciones")

    # --- GENERAR INFORME ---
    logger.info("\n--- Generando Informe ---")
    report = generate_report(precios_data, lecciones_data, all_errors)

    # Guardar informe en archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = paths['base'] / f'informe_{timestamp}.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    logger.info(f"Informe guardado en: {report_path}")

    # Mostrar informe en consola
    print("\n")
    print(report)

    # Resumen final
    logger.info("\n" + "=" * 60)
    logger.info("SCRAPING COMPLETADO")
    logger.info(f"Resultados guardados en: {paths['base']}")
    logger.info("=" * 60)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("\nProceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error fatal: {e}", exc_info=True)
        sys.exit(1)

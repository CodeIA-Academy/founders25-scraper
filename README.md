# CodeIA Scraper

Scraper para extraer información de [codeia.dev](https://codeia.dev).

## Versión

0.2.0

## Descripción

Este scraper extrae información de dos secciones principales de CodeIA:

- **Precios** (`/precios`): Planes y características
- **Lecciones** (`/lecciones`): Títulos, descripciones, etiquetas, fechas, visualizaciones, categorías, imágenes de portada y URLs de videos

## Características

- ✅ Scraping con Selenium (soporte para contenido dinámico)
- ✅ Descarga automática de imágenes
- ✅ Exportación a CSV y JSON
- ✅ Generación de informes detallados
- ✅ Manejo robusto de errores
- ✅ Logging completo

## Instalación

1. Crear entorno virtual de Python:

```bash
python3 -m venv venv
```

2. Activar el entorno virtual:

```bash
source venv/bin/activate
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. Asegúrate de tener Chrome/Chromium instalado (para Selenium)

## Uso

### Opción 1: Con script auxiliar

```bash
./run.sh
```

### Opción 2: Manual

1. Activar entorno virtual:
```bash
source venv/bin/activate
```

2. Ejecutar el scraper:
```bash
python main.py
```

3. Desactivar entorno virtual:
```bash
deactivate
```

## Estructura de Salida

El scraper genera los siguientes archivos en la carpeta `output/`:

```
output/
├── data/
│   ├── precios.json        # Datos de precios en JSON
│   ├── precios.csv         # Datos de precios en CSV
│   ├── lecciones.json      # Datos de lecciones en JSON
│   └── lecciones.csv       # Datos de lecciones en CSV
├── images/
│   ├── precios/            # Imágenes de planes (si aplica)
│   └── lecciones/          # Imágenes de portada de lecciones
└── informe_YYYYMMDD_HHMMSS.txt  # Informe detallado del scraping
```

## Formato de Datos

### Precios (JSON/CSV)

```json
{
  "nombre": "Plan Pro",
  "precio": "$99/mes",
  "caracteristicas": ["Feature 1", "Feature 2"],
  "num_caracteristicas": 2
}
```

### Lecciones (JSON/CSV)

```json
{
  "titulo": "Introducción a IA",
  "descripcion": "Aprende los fundamentos...",
  "etiquetas": ["IA", "Python"],
  "fecha": "2024-01-15",
  "visualizaciones": "1500",
  "categoria": "Fundamentos",
  "imagen_portada": "introduccion-a-ia.jpg",
  "imagen_url": "https://codeia.dev/images/...",
  "url_video": "https://codeia.dev/lecciones/..."
}
```

## Desarrollo

Este proyecto utiliza Conventional Commits para mantener un historial de cambios semántico.

### Tipos de commits

- `feat`: Nueva funcionalidad
- `fix`: Corrección de errores
- `docs`: Cambios en documentación
- `style`: Cambios de formato (sin afectar el código)
- `refactor`: Refactorización de código
- `test`: Añadir o modificar tests
- `chore`: Cambios en el proceso de build o herramientas auxiliares

## Licencia

MIT

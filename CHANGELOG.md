# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [0.2.0] - 2025-11-13

### Añadido
- Scraper funcional para página de lecciones con extracción completa de datos
- Scraper funcional para página de precios con extracción de planes y características
- Descarga automática de imágenes de portada de lecciones
- Exportación de datos a formato CSV y JSON
- Generación de informes detallados con resumen de scraping
- Sistema de logging completo
- Entorno virtual de Python configurado
- Script auxiliar `run.sh` para ejecución rápida
- Manejo robusto de errores con ChromeDriver
- Soporte para contenido dinámico con Selenium

### Características Extraídas
- **Lecciones**: título, descripción, etiquetas, fecha, visualizaciones, categoría, duración, imagen de portada, URL del video
- **Precios**: nombre del plan, precio, características

## [0.1.0] - 2025-11-13

### Añadido
- Configuración inicial del proyecto
- Estructura base de carpetas
- Configuración de Commitizen para versionado semántico
- README con documentación básica
- Configuración de .gitignore para Python
- Requirements.txt con dependencias iniciales

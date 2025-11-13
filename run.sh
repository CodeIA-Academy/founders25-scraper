#!/bin/bash

# Script para ejecutar el scraper con el entorno virtual activado

# Activar entorno virtual
source venv/bin/activate

# Ejecutar scraper
python main.py

# Desactivar entorno virtual
deactivate

#!/bin/bash

# Script de configuración para entornos Linux/macOS
echo "--- Configurando entorno virtual 'venv' ---"

# Verificar si python3 está instalado
if ! command -v python3 &> /dev/null
then
    echo "Error: python3 no está instalado."
    exit
fi

# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
echo "--- Instalando dependencias desde requirements.txt ---"
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Configuración completada."
echo "Para activar el entorno manualmente use: source venv/bin/activate"

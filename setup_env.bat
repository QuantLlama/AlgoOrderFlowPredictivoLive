@echo off
echo ==========================================
echo  Configurando Entorno Virtual Python
echo ==========================================

:: 1. Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  Python no encontrado. Por favor instala Python y agregalo al PATH.
    pause
    exit /b
)

:: 2. Crear venv si no existe
if not exist "venv" (
    echo --> Creando entorno virtual 'venv'...
    python -m venv venv
) else (
    echo --> El entorno virtual 'venv' ya existe.
)

:: 3. Activar e instalar
echo --> Activando entorno e instalando dependencias...
call venv\Scripts\activate
pip install --upgrade pip
if exist "requirements.txt" (
    pip install -r requirements.txt
    echo  Dependencias instaladas correctamente.
) else (
    echo  No se encontro requirements.txt
)

echo.
echo ==========================================
echo Instalacion completada!
echo Para activar manualmente usa: venv\Scripts\activate
echo ==========================================
pause

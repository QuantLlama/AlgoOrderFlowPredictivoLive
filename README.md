# 🚀 AlgoOrderFlowPredictivoLive

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![NinjaTrader 8](https://img.shields.io/badge/Platform-NinjaTrader%208-orange.svg)](https://ninjatrader.com/)

**AlgoOrderFlowPredictivoLive** es una solución avanzada de trading automatizado diseñada para futuros de índices (específicamente optimizada para **MNQ/NQ**). Combina el análisis de **Microestructura de Mercado** y **Order Flow** para identificar oportunidades de alta probabilidad.

---

## 📋 Tabla de Contenidos
- [Lógica de la Estrategia](#-lógica-de-la-estrategia)
- [Gestión de Riesgo](#-gestión-de-riesgo)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Instalación y Configuración](#-instalación-y-configuración)
- [Uso](#-uso) 
- [Licencia](#-licencia)
- [Contacto](#-contacto)

---

## 🧠 Lógica de la Estrategia

El algoritmo detecta **huellas institucionales** mediante el análisis de:

1.  **Absorción (Reversión)**: Identificación de liquidez pasiva que detiene movimientos agresivos (mechas largas con volumen inusual).
2.  **Breakout (Continuación)**: Confirmación de rupturas mediante inyección de liquidez agresiva.
3.  **Filtros de Calidad**:
    *   **EMA 200**: Filtro de tendencia macro.
    *   **RSI Dinámico**: Filtro de condiciones extremas (sobrecompra/sobreventa).
    *   **Volumen Relativo**: Validación de señales mediante participación real del mercado.

---

## 🛡️ Gestión de Riesgo (Money Management)

Implementa una gestión profesional del capital:
*   **Stop Loss Adaptativo**: Basado en la volatilidad actual (ATR/Rango).
*   **Target dinámico**: Ratio Riesgo/Beneficio optimizado (1:2.2).
*   **Salida por Tiempo**: Cierre automático tras 12 velas (1 hora) si no se alcanza el objetivo.

---

## 📂 Estructura del Proyecto

```text
AlgoOrderFlowPredictivoLive/
├── Automatizacion_NinjaScript/  # Scripts para NinjaTrader 8 (.cs)
│   └── OrderFlowPredictivo.cs   # Lógica principal en C#
├── OrderFlowPredictivo.py       # Versión de análisis/backtest en Python
├── requirements.txt             # Dependencias de Python
├── setup_env.sh                 # Configuración automática (Linux/macOS)
├── setup_env.bat                # Configuración automática (Windows)
├── LICENSE                      # Licencia MIT
└── README.md                    # Documentación
```

---

## 🛠️ Instalación y Configuración

### 1. NinjaTrader 8
1. Copia `Automatizacion_NinjaScript/OrderFlowPredictivo.cs` a:
   `Documentos\NinjaTrader 8\bin\Custom\Strategies`
2. Abre NinjaTrader y compila (F5 en el editor de script).

### 2. Entorno Python (Análisis/Backtest)
Ejecuta el script de configuración según tu sistema:

**Windows:**
```bash
setup_env.bat
```

**Linux/macOS:**
```bash
./setup_env.sh
```

---

## 🚀 Uso

1.  **Instrumento**: Futuros Nasdaq (MNQ/NQ).
2.  **Temporalidad**: 5 Minutos (M5).
3.  **Sesión**: Preferiblemente Sesión Americana (RTH).

---

## ⚖️ Licencia

Este proyecto está bajo la Licencia **MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

## 📩 Contacto

**Ing. Pablo Ez. Moscardo** - *NBNSystemas - Punto&ComaTrading*
*   **Sitio Web**: [llamaia.nbmsystemas.com](https://llamaia.nbmsystemas.com)
*   **E-mail**: contacto@nbmsystemas.com / pablo.ezequiel.moscardo@gmail.com
*   **YouTube**: [@puntoicomatrading](https://youtube.com/@puntoicomatrading)

---
*Desarrollado por Quantun LLAMA IA © 2026*

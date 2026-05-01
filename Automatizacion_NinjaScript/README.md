# OrderFlowPredictivo (NinjaTrader 8 Strategy)

Este algoritmo es una estrategia de trading automatizada diseñada para capturar movimientos de alta probabilidad en futuros de índices (específicamente optimizada para **MNQ/NQ**), basándose en principios de **Microestructura de Mercado** y **Order Flow** simulado.

## Lógica de la Estrategia

El sistema no utiliza indicadores tradicionales de forma aislada, sino que busca **huellas institucionales** en el precio y el volumen.

### 1. Filosofía de Entrada
El algoritmo busca dos tipos de eventos de mercado:
*   **Absorción (Reversión)**: Detecta cuando el precio intenta romper un nivel con fuerza (alto volumen) pero es rechazado violentamente (mechas largas). Esto indica que hay liquidez pasiva absorbiendo la agresión.
*   **Breakout (Continuación)**: Detecta velas de cuerpo grande y alto volumen que rompen máximos o mínimos recientes, indicando una inyección de liquidez agresiva a favor de la ruptura.

### 2. Filtros de Calidad
Para evitar señales falsas, el sistema aplica un estricto filtrado:
*   **Tendencia Macro (EMA 200)**: Solo opera Long si el precio está sobre la EMA 200, y Short si está por debajo. **(La media está oculta en el gráfico para limpieza visual)**.
*   **RSI Inteligente**: Evita comprar si el mercado ya está sobrecomprado (>70) o vender si está sobrevendido (<30).
*   **Volumen Relativo**: Las señales solo son válidas si el volumen es significativamente superior al promedio de las últimas 20 velas.

##  Gestión de Riesgo (Money Management)

Esta es la parte más robusta del sistema, diseñada para proteger el capital como un trader humano profesional:

*   **Stop Loss Dinámico**: No es un número fijo. Se calcula en cada operación basándose en la volatilidad de la vela de entrada (Rango * 1.2).
*   **Ratio Riesgo/Beneficio**: Busca ganar **2.2 veces** lo arriesgado (Ratio 1:2.2).
*   **Time Stop (Salida por Tiempo)**: Si la operación no alcanza el objetivo ni el stop en **12 velas (1 hora)**, se cierra automáticamente. Esto evita tener capital estancado en mercados laterales ("zombies").

##  Configuración Recomendada

*   **Instrumento**: Futuros del Nasdaq (MNQ para cuentas pequeñas, NQ para grandes).
*   **Temporalidad**: **5 Minutos (M5)**. La lógica de absorción y time stop está calibrada para este timeframe.
*   **Capital Recomendado**:
    *   **MNQ (Micro)**: Mínimo $1,000 - Recomendado $3,000+.
    *   **NQ (Mini)**: Mínimo $15,000 - Recomendado $25,000+.
*   **Horario**: Funciona mejor durante la sesión americana (RTH) donde hay mayor volumen real.

##  Instalación

1.  Copia el archivo `OrderFlowPredictivo.cs` en tu carpeta de estrategias de NinjaTrader:
    `Documentos\NinjaTrader 8\bin\Custom\Strategies`
2.  Abre NinjaTrader y compila (F5 en el editor de script).
3.  Abre un gráfico de 5 minutos, añade la estrategia y asegúrate de habilitar "Enabled".

---

## Licencia y Autoría

Este proyecto se distribuye como **Open Source** para fines educativos y de desarrollo personal. Sin embargo, la **autoría intelectual original** de la estrategia y el código pertenecen a su creador.

Se permite su uso, modificación y distribución libremente, siempre y cuando se reconozca la autoría original.

*Desarrollado con un enfoque de código limpio y lógica "humana" para facilitar su auditoría y mejora, Ing. Pablo Ez. Moscardo - NBNSystemas - Punto&ComaTrading - Quantun LlamaIA*

                https://llamaia.nbmsystemas.com - https://nbmsystemas.com - Youtube/@puntoicomatrading

                      E-mail: contacto@nbmsystemas.com - pablo.ezequiel.moscardo@gmail.com

                    Quantun LLAMA IA  © 2026 LLAMA IA. Inteligencia Artificial para Trading.
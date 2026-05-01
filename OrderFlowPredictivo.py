
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import warnings

# Ignorar advertencias molestas
warnings.filterwarnings('ignore')

# Configuración de estilo para los gráficos
plt.style.use('dark_background')
plt.rcParams['figure.figsize'] = (14, 8)

class SistemaPredictivo:
    def __init__(self, ticker="MNQ=F", capital_inicial=10000):
        self.ticker = ticker
        self.capital = capital_inicial
        self.equity = [capital_inicial]
        self.trades = []
        self.df = None
        
        # Parámetros de la estrategia (ajustables)
        self.timeframe = "5m"
        self.periodo = "60d"
        self.riesgo_por_trade = 0.015  # 1.5% de riesgo
        self.min_stop_pts = 10         # Mínimo stop loss en puntos
        
    def cargar_datos(self):
        print(f"--> Cargando datos para {self.ticker}...")
        try:
            self.df = yf.download(self.ticker, period=self.periodo, interval=self.timeframe, progress=False)
            
            # Ajuste feo para multi-index columns de yfinance
            if isinstance(self.df.columns, pd.MultiIndex):
                self.df.columns = self.df.columns.get_level_values(0)
                
            self.df = self.df[['Open', 'High', 'Low', 'Close', 'Volume']]
            self.df.dropna(inplace=True)
            print(f"--> Datos OK: {len(self.df)} velas importadas.")
            
        except Exception as e:
            print(f"Error cargando datos: {e}")
            
    def analizar_microestructura(self):
        # Aquí calculamos métricas de Order Flow y estructura
        # No es perfecto, pero nos da una idea de la presión
        
        df = self.df
        
        # 1. Definir velas alcistas/bajistas y su cuerpo
        df['Cuerpo'] = abs(df['Close'] - df['Open'])
        df['MechaSup'] = df['High'] - df[['Open', 'Close']].max(axis=1)
        df['MechaInf'] = df[['Open', 'Close']].min(axis=1) - df['Low']
        
        # 2. Delta aproximado (Volumen * Dirección)
        # Asumimos que si cierra arriba, la mayoría del volumen fue compra
        df['Direccion'] = np.where(df['Close'] >= df['Open'], 1, -1)
        df['Delta'] = df['Volume'] * df['Direccion']
        
        # Cumulative Delta para ver la tendencia de fondo
        df['CumDelta'] = df['Delta'].rolling(window=20).sum()
        
        # 3. Eficiencia del precio
        # Cuánto se mueve el precio por unidad de volumen
        df['Rango'] = df['High'] - df['Low']
        df['Eficiencia'] = df['Rango'] / (df['Volume'] + 1)
        
        # 4. Detectar zonas de absorción (Mechas largas con mucho volumen)
        vol_promedio = df['Volume'].rolling(20).mean()
        
        # Absorción Bajista: Mecha superior larga + Volumen alto + Cierre lejos del High
        df['Absorcion_Venta'] = (
            (df['MechaSup'] > df['Cuerpo'] * 1.5) & 
            (df['Volume'] > vol_promedio * 1.2)
        )
        
        # Absorción Alcista: Mecha inferior larga + Volumen alto + Cierre lejos del Low
        df['Absorcion_Compra'] = (
            (df['MechaInf'] > df['Cuerpo'] * 1.5) & 
            (df['Volume'] > vol_promedio * 1.2)
        )
        
        # 5. Tendencia de corto plazo (EMA)
        df['EMA_50'] = df['Close'].ewm(span=50).mean()
        df['EMA_200'] = df['Close'].ewm(span=200).mean() # Tendencia principal
        df['Distancia_EMA'] = (df['Close'] - df['EMA_50'])
        
        # 6. RSI para evitar entrar en extremos
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        self.df = df.dropna()

    def generar_senales(self):
        df = self.df
        df['Signal'] = 0
        
        # Lógica de entrada más humana:
        # Buscamos "reversiones" en zonas extremas o "continuación" con fuerza
        
        for i in range(1, len(df)):
            # Contexto
            vela_actual = df.iloc[i]
            
            # FILTRO DE TENDENCIA: EMA 200 es clave
            tendencia_alcista = vela_actual['Close'] > vela_actual['EMA_200']
            tendencia_bajista = vela_actual['Close'] < vela_actual['EMA_200']
            
            # Filtro RSI (No comprar si está sobrecomprado > 70, no vender si sobrevendido < 30)
            rsi_ok_long = vela_actual['RSI'] < 70
            rsi_ok_short = vela_actual['RSI'] > 30
            
            # === SEÑAL DE COMPRA (LONG) ===
            # Caso 1: Absorción de venta en soporte (Reversión) + Delta positivo reciente
            if (vela_actual['Absorcion_Compra'] and 
                vela_actual['Delta'] > 0 and 
                tendencia_alcista and
                rsi_ok_long):
                df.at[df.index[i], 'Signal'] = 1
                
            # Caso 2: Breakout con fuerza (Vela grande, rompe rango previo)
            elif (vela_actual['Cuerpo'] > vela_actual['Rango'] * 0.8 and 
                  vela_actual['Close'] > df['High'].iloc[i-10:i].max() and # Rompe max de 10 velas
                  vela_actual['Volume'] > vela_actual['Volume'] * 1.5 and # Mucho volumen
                  tendencia_alcista): 
                df.at[df.index[i], 'Signal'] = 1

            # === SEÑAL DE VENTA (SHORT) ===
            # Caso 1: Absorción de compra en resistencia
            elif (vela_actual['Absorcion_Venta'] and 
                  vela_actual['Delta'] < 0 and
                  tendencia_bajista and
                  rsi_ok_short):
                df.at[df.index[i], 'Signal'] = -1
                
            # Caso 2: Breakdown con fuerza
            elif (vela_actual['Cuerpo'] > vela_actual['Rango'] * 0.8 and
                  vela_actual['Close'] < df['Low'].iloc[i-10:i].min() and
                  vela_actual['Volume'] > vela_actual['Volume'] * 1.5 and
                  tendencia_bajista):
                df.at[df.index[i], 'Signal'] = -1
                
        self.df = df

    def ejecutar_backtest(self):
        print("--> Ejecutando simulación de trading...")
        
        balance = self.capital
        posicion = None # {type: 1/-1, entry: float, stop: float, target: float, size: float}
        
        historial = []
        equity_curve = [balance]
        
        for i in range(len(self.df) - 1):
            # Datos actuales (al cierre de la vela i, operamos en i+1 open)
            timestamp = self.df.index[i]
            row = self.df.iloc[i]
            next_open = self.df.iloc[i+1]['Open']
            next_high = self.df.iloc[i+1]['High']
            next_low = self.df.iloc[i+1]['Low']
            
            # 1. GESTIÓN DE POSICIÓN ABIERTA
            if posicion is not None:
                resultado = 0
                cerrada = False
                posicion['bars_held'] += 1
                
                # Chequear Time Stop (12 velas = 1 hora)
                if posicion['bars_held'] >= 12:
                    current_close = row['Close']
                    if posicion['type'] == 1:
                        resultado = (current_close - posicion['entry']) * posicion['size']
                    else:
                        resultado = (posicion['entry'] - current_close) * posicion['size']
                    cerrada = True
                    tipo_cierre = "Time Stop (1h)"
                
                # Chequear Stops y Targets
                # Asumimos el peor caso primero para ser conservadores (tocar stop antes que target)
                
                # LONG
                if not cerrada and posicion['type'] == 1:
                    if next_low <= posicion['stop']: # Stop Loss hit
                        resultado = (posicion['stop'] - posicion['entry']) * posicion['size']
                        cerrada = True
                        tipo_cierre = "Stop Loss"
                    elif next_high >= posicion['target']: # Take Profit hit
                        resultado = (posicion['target'] - posicion['entry']) * posicion['size']
                        cerrada = True
                        tipo_cierre = "Take Profit"
                        
                # SHORT
                elif not cerrada and posicion['type'] == -1:
                    if next_high >= posicion['stop']: # Stop Loss hit
                        resultado = (posicion['entry'] - posicion['stop']) * posicion['size']
                        cerrada = True
                        tipo_cierre = "Stop Loss"
                    elif next_low <= posicion['target']: # Take Profit hit
                        resultado = (posicion['entry'] - posicion['target']) * posicion['size']
                        cerrada = True
                        tipo_cierre = "Take Profit"
                
                if cerrada:
                    balance += resultado
                    historial.append({
                        'fecha': timestamp,
                        'tipo': 'Long' if posicion['type'] == 1 else 'Short',
                        'resultado': resultado,
                        'balance': balance,
                        'motivo': tipo_cierre
                    })
                    posicion = None
            
            # 2. BUSCAR NUEVA ENTRADA (Solo si no hay posición)
            if posicion is None:
                signal = row['Signal']
                
                if signal != 0:
                    # Gestión de Riesgo
                    atr = row['Rango'] # Usamos el rango de la vela actual como proxy de volatilidad
                    stop_dist = max(atr * 1.2, self.min_stop_pts) # Mínimo 10 puntos de stop
                    target_dist = stop_dist * 2.2 # Ratio 1:2.2 (Más ambicioso)
                    
                    riesgo_monetario = balance * self.riesgo_por_trade
                    size = riesgo_monetario / stop_dist
                    
                    if signal == 1:
                        posicion = {
                            'type': 1,
                            'entry': next_open,
                            'stop': next_open - stop_dist,
                            'target': next_open + target_dist,
                            'size': size,
                            'bars_held': 0 # Para time stop
                        }
                    else:
                        posicion = {
                            'type': -1,
                            'entry': next_open,
                            'stop': next_open + stop_dist,
                            'target': next_open - target_dist,
                            'size': size,
                            'bars_held': 0
                        }

            equity_curve.append(balance)
            
        # Guardar resultados
        self.trades = pd.DataFrame(historial)
        self.equity = equity_curve
        
        # Resultados finales
        self.imprimir_estadisticas()

    def imprimir_estadisticas(self):
        if len(self.trades) == 0:
            print("No se hicieron trades. Intenta cambiar los parámetros.")
            return
            
        ganadoras = self.trades[self.trades['resultado'] > 0]
        perdedoras = self.trades[self.trades['resultado'] <= 0]
        
        win_rate = len(ganadoras) / len(self.trades) * 100
        avg_win = ganadoras['resultado'].mean() if not ganadoras.empty else 0
        avg_loss = perdedoras['resultado'].mean() if not perdedoras.empty else 0
        
        profit_factor = abs(ganadoras['resultado'].sum() / perdedoras['resultado'].sum()) if perdedoras['resultado'].sum() != 0 else 999
        
        retorno_total = (self.equity[-1] - self.capital) / self.capital * 100
        
        # Métricas adicionales (Drawdown)
        equity_series = pd.Series(self.equity)
        peak = equity_series.expanding().max()
        dd = (equity_series - peak) / peak * 100
        max_dd = dd.min()

        print("\n" + "="*50)
        print("## RESULTADOS DE LA ESTRATEGIA (VERSIÓN 2.1) ##")
        print("="*50)
        print(f"== Capital Final ==    : ${self.equity[-1]:,.2f}")
        print(f"== Retorno Total ==    : {retorno_total:.2f}%")
        print(f"== Max Drawdown ==     : {max_dd:.2f}%")
        print("-" * 50)
        print(f"== Total Trades ==     : {len(self.trades)}")
        print(f"== Win Rate ==         : {win_rate:.2f}%")
        print(f"== Profit Factor ==    : {profit_factor:.2f}")
        print(f"== Avg Win ==          : ${avg_win:.2f}")
        print(f"== Avg Loss ==         : ${avg_loss:.2f}")
        print("="*50)
        
        # Graficar
        self.plot_equity()

    def plot_equity(self):
        plt.figure(figsize=(12, 6))
        plt.plot(self.equity, label='Equity Curve', color='cyan')
        plt.axhline(y=self.capital, color='white', linestyle='--', alpha=0.3)
        plt.title('Crecimiento de la Cuenta')
        plt.xlabel('Trades / Tiempo')
        plt.ylabel('Capital ($)')
        plt.legend()
        plt.grid(True, alpha=0.2)
        plt.show()

# ==========================================
# EJECUCIÓN
# ==========================================
if __name__ == "__main__":
    # Instanciamos el sistema
    bot = SistemaPredictivo(ticker="MNQ=F", capital_inicial=10000)
    
    # Corremos el pipeline
    bot.cargar_datos()
    bot.analizar_microestructura()
    bot.generar_senales()
    bot.ejecutar_backtest()

#region Using declarations
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;
using System.Windows.Media;
using System.Xml.Serialization;
using NinjaTrader.Cbi;
using NinjaTrader.Gui;
using NinjaTrader.Gui.Chart;
using NinjaTrader.Gui.SuperDom;
using NinjaTrader.Gui.Tools;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
using NinjaTrader.Core.FloatingPoint;
using NinjaTrader.NinjaScript.Indicators;
using NinjaTrader.NinjaScript.DrawingTools;
#endregion

// This namespace holds Strategies in this folder and is required. Do not change it. 
namespace NinjaTrader.NinjaScript.Strategies
{
    public class OrderFlowPredictivo : Strategy
    {
        // ==========================================
        // VARIABLES E INDICADORES
        // ==========================================
        private EMA ema50;
        private EMA ema200;
        private RSI rsi;
        private SMA volSMA;

        // Variables de gestión de la operación
        private int barsHeld = 0;
        private double stopPrice = 0;
        private double targetPrice = 0;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description                                 = @"Estrategia portada de Python (v2.1): Combina estructura de mercado, absorción de volumen y gestión de riesgo dinámica.";
                Name                                        = "OrderFlowPredictivo";
                Calculate                                   = Calculate.OnBarClose; // Calculamos al cierre de vela (igual que el script original)
                EntriesPerDirection                         = 1;
                EntryHandling                               = EntryHandling.AllEntries;
                IsExitOnSessionCloseStrategy                = true;
                ExitOnSessionCloseSeconds                   = 30;
                IsFillLimitOnTouch                          = false;
                MaximumBarsLookBack                         = MaximumBarsLookBack.TwoHundredFiftySix;
                OrderFillResolution                         = OrderFillResolution.Standard;
                Slippage                                    = 0;
                StartBehavior                               = StartBehavior.WaitUntilFlat;
                TimeInForce                                 = TimeInForce.Gtc;
                TraceOrders                                 = false;
                RealtimeErrorHandling                       = RealtimeErrorHandling.StopCancelClose;
                StopTargetHandling                          = StopTargetHandling.PerEntryExecution;
                BarsRequiredToTrade                         = 200; // Necesario para EMA 200
                
                // Parámetros por defecto editables desde la UI
                CapitalInicial = 10000;
                RiesgoPorTrade = 1.5; // 1.5% de riesgo
                MinStopPoints = 10.0; // Mínimo stop en puntos
            }
            else if (State == State.Configure)
            {
                // Inicializamos los indicadores
                // EMA 50 y 200 para tendencia
                ema50 = EMA(50);
                ema200 = EMA(200);
                
                // RSI 14 para detectar extremos
                rsi = RSI(14, 3);
                
                // SMA de Volumen para detectar picos relativos
                volSMA = SMA(Volume, 20);
                
                // Las medias se calculan en memoria pero NO se dibujan en el gráfico
                // para mantener la pantalla limpia.
                // AddChartIndicator(ema50);
                // AddChartIndicator(ema200);
            }
        }

        protected override void OnBarUpdate()
        {
            // Esperar a tener suficientes datos
            if (CurrentBar < 200) return;

            // ==========================================
            // 1. DATOS DE LA VELA ACTUAL
            // ==========================================
            double open = Open[0];
            double close = Close[0];
            double high = High[0];
            double low = Low[0];
            double volumen = Volume[0];
            
            // Métricas de la vela
            double range = high - low;
            double body = Math.Abs(close - open);
            double mechaSup = high - Math.Max(open, close);
            double mechaInf = Math.Min(open, close) - low;
            
            // ==========================================
            // 2. CONTEXTO DE MERCADO
            // ==========================================
            double avgVol = volSMA[0];
            
            // Filtros de Tendencia (Solo operamos a favor de la EMA 200)
            bool tendenciaAlcista = close > ema200[0];
            bool tendenciaBajista = close < ema200[0];
            
            // Filtros RSI (Evitar comprar en techo o vender en suelo)
            bool rsiOkLong = rsi[0] < 70;
            bool rsiOkShort = rsi[0] > 30;
            
            // "Delta Simulado": Si cierra arriba, asumimos presión compradora
            double delta = (close >= open) ? volumen : -volumen;

            // ==========================================
            // 3. GESTIÓN DE POSICIÓN EXISTENTE
            // ==========================================
            if (Position.MarketPosition != MarketPosition.Flat)
            {
                barsHeld++;
                
                // TIME STOP: Si en 12 velas (1 hora en M5) no funciona, cerramos.
                // Esto libera capital y evita "trades zombies".
                if (barsHeld >= 12)
                {
                    if (Position.MarketPosition == MarketPosition.Long)
                        ExitLong("TimeStop_Exit");
                    else
                        ExitShort("TimeStop_Exit");
                    
                    return; // Salimos de la lógica por esta barra
                }
            }
            else
            {
                barsHeld = 0;
            }

            // ==========================================
            // 4. LÓGICA DE SEÑALES (ENTRY)
            // ==========================================
            if (Position.MarketPosition == MarketPosition.Flat)
            {
                bool signalLong = false;
                bool signalShort = false;

                // --- SETUP A: Absorción (Reversión en soporte/resistencia) ---
                // Buscamos mechas largas con mucho volumen
                bool absorcionCompra = (mechaInf > body * 1.5) && (volumen > avgVol * 1.2);
                bool absorcionVenta = (mechaSup > body * 1.5) && (volumen > avgVol * 1.2);

                if (absorcionCompra && delta > 0 && tendenciaAlcista && rsiOkLong)
                    signalLong = true;
                
                if (absorcionVenta && delta < 0 && tendenciaBajista && rsiOkShort)
                    signalShort = true;

                // --- SETUP B: Breakout (Continuación de fuerza) ---
                // Vela de cuerpo grande que rompe máximos/mínimos recientes
                double max10 = MAX(High, 10)[1]; // Máximo de las 10 anteriores
                double min10 = MIN(Low, 10)[1]; // Mínimo de las 10 anteriores
                
                bool breakoutFuerte = (body > range * 0.8) && (volumen > avgVol * 1.5);
                
                if (breakoutFuerte && close > max10 && tendenciaAlcista)
                    signalLong = true;
                    
                if (breakoutFuerte && close < min10 && tendenciaBajista)
                    signalShort = true;

                // ==========================================
                // 5. EJECUCIÓN DE ÓRDENES
                // ==========================================
                if (signalLong)
                {
                    // Cálculo de Stop Loss Dinámico
                    // Usamos el rango de la vela (volatilidad) pero respetando un mínimo
                    double stopDist = Math.Max(range * 1.2, MinStopPoints); 
                    
                    // Ratio Riesgo:Beneficio de 1:2.2 (Arriesgas 1 para ganar 2.2)
                    double targetDist = stopDist * 2.2;
                    
                    stopPrice = close - stopDist;
                    targetPrice = close + targetDist;
                    
                    // Configuramos las salidas ANTES de entrar
                    SetStopLoss(CalculationMode.Price, stopPrice);
                    SetProfitTarget(CalculationMode.Price, targetPrice);
                    
                    // Calculamos tamaño de posición (simple para NT: 1 contrato por defecto)
                    // En un entorno real aquí calcularías Quantity = (Capital * Riesgo) / StopDist
                    EnterLong("Long_Setup");
                }
                else if (signalShort)
                {
                    double stopDist = Math.Max(range * 1.2, MinStopPoints); 
                    double targetDist = stopDist * 2.2;
                    
                    stopPrice = close + stopDist;
                    targetPrice = close - targetDist;
                    
                    SetStopLoss(CalculationMode.Price, stopPrice);
                    SetProfitTarget(CalculationMode.Price, targetPrice);
                    
                    EnterShort("Short_Setup");
                }
            }
        }

        #region Properties
        [NinjaScriptProperty]
        [Range(1, int.MaxValue)]
        [Display(Name="Capital Inicial", Order=1, GroupName="Parámetros Generales")]
        public double CapitalInicial
        { get; set; }

        [NinjaScriptProperty]
        [Range(0.1, 10.0)]
        [Display(Name="Riesgo % por Trade", Order=2, GroupName="Parámetros Generales")]
        public double RiesgoPorTrade
        { get; set; }
        
        [NinjaScriptProperty]
        [Range(1.0, 100.0)]
        [Display(Name="Mínimo Stop (Puntos)", Order=3, GroupName="Parámetros Generales")]
        public double MinStopPoints
        { get; set; }
        #endregion
    }
}

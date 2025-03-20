from typing import Dict, Any, List
import pandas as pd
import numpy as np
import ccxt
import ta
from datetime import datetime, timedelta
from ..core.base_agent import BaseAgent

class TechnicalAgent(BaseAgent):
    """Agente para análise técnica de tokens"""
    
    def __init__(self):
        super().__init__()
        self.description = "Agente especializado em análise técnica de tokens"
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot'
            }
        })
        
    async def validate_input(self, token_data: Dict[str, Any]) -> bool:
        """
        Valida os dados de entrada do token.
        
        Args:
            token_data: Dados do token para validação
            
        Returns:
            bool: True se os dados são válidos, False caso contrário
        """
        required_fields = ['symbol', 'timeframe']
        return all(field in token_data for field in required_fields)
    
    async def analyze(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza análise técnica do token.
        
        Args:
            token_data: Dados do token para análise
            
        Returns:
            Dict[str, Any]: Resultado da análise técnica
        """
        try:
            # Obtém dados históricos
            ohlcv = await self._fetch_historical_data(
                token_data['symbol'],
                token_data['timeframe']
            )
            
            # Calcula indicadores técnicos
            indicators = self._calculate_indicators(ohlcv)
            
            # Gera sinais
            signals = self._generate_signals(indicators)
            
            # Análise de tendência
            trend_analysis = self._analyze_trend(indicators)
            
            # Níveis de suporte e resistência
            levels = self._find_support_resistance(ohlcv)
            
            return {
                "indicators": indicators,
                "signals": signals,
                "trend_analysis": trend_analysis,
                "support_resistance": levels,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _fetch_historical_data(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """Obtém dados históricos do token"""
        try:
            # Ajusta o símbolo para o formato da exchange
            formatted_symbol = f"{symbol}/USDT"
            
            # Obtém dados históricos
            ohlcv = self.exchange.fetch_ohlcv(
                formatted_symbol,
                timeframe=timeframe,
                limit=100
            )
            
            # Converte para DataFrame
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            
            # Converte timestamp para datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            return df
            
        except Exception as e:
            raise Exception(f"Erro ao obter dados históricos: {str(e)}")
    
    def _calculate_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calcula indicadores técnicos"""
        try:
            # RSI
            df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()
            
            # MACD
            macd = ta.trend.MACD(df['close'])
            df['macd'] = macd.macd()
            df['macd_signal'] = macd.macd_signal()
            df['macd_diff'] = macd.macd_diff()
            
            # Bollinger Bands
            bollinger = ta.volatility.BollingerBands(df['close'])
            df['bb_high'] = bollinger.bollinger_hband()
            df['bb_low'] = bollinger.bollinger_lband()
            df['bb_mid'] = bollinger.bollinger_mavg()
            
            # Médias Móveis
            df['sma_20'] = ta.trend.SMAIndicator(df['close'], window=20).sma_indicator()
            df['sma_50'] = ta.trend.SMAIndicator(df['close'], window=50).sma_indicator()
            df['sma_200'] = ta.trend.SMAIndicator(df['close'], window=200).sma_indicator()
            
            # Volume
            df['volume_sma'] = ta.trend.SMAIndicator(df['volume'], window=20).sma_indicator()
            
            # Retorna últimos valores
            last_row = df.iloc[-1]
            return {
                "rsi": float(last_row['rsi']),
                "macd": {
                    "macd": float(last_row['macd']),
                    "signal": float(last_row['macd_signal']),
                    "diff": float(last_row['macd_diff'])
                },
                "bollinger_bands": {
                    "high": float(last_row['bb_high']),
                    "low": float(last_row['bb_low']),
                    "middle": float(last_row['bb_mid'])
                },
                "moving_averages": {
                    "sma_20": float(last_row['sma_20']),
                    "sma_50": float(last_row['sma_50']),
                    "sma_200": float(last_row['sma_200'])
                },
                "volume": {
                    "current": float(last_row['volume']),
                    "sma": float(last_row['volume_sma'])
                }
            }
            
        except Exception as e:
            raise Exception(f"Erro ao calcular indicadores: {str(e)}")
    
    def _generate_signals(self, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Gera sinais de trading baseados nos indicadores"""
        signals = {
            "rsi": "neutral",
            "macd": "neutral",
            "bollinger": "neutral",
            "moving_averages": "neutral",
            "volume": "neutral"
        }
        
        # RSI
        if indicators['rsi'] > 70:
            signals['rsi'] = "sell"
        elif indicators['rsi'] < 30:
            signals['rsi'] = "buy"
            
        # MACD
        if indicators['macd']['diff'] > 0 and indicators['macd']['macd'] > indicators['macd']['signal']:
            signals['macd'] = "buy"
        elif indicators['macd']['diff'] < 0 and indicators['macd']['macd'] < indicators['macd']['signal']:
            signals['macd'] = "sell"
            
        # Bollinger Bands
        current_price = indicators['bollinger_bands']['middle']
        if current_price > indicators['bollinger_bands']['high']:
            signals['bollinger'] = "sell"
        elif current_price < indicators['bollinger_bands']['low']:
            signals['bollinger'] = "buy"
            
        # Moving Averages
        if (indicators['moving_averages']['sma_20'] > indicators['moving_averages']['sma_50'] > 
            indicators['moving_averages']['sma_200']):
            signals['moving_averages'] = "buy"
        elif (indicators['moving_averages']['sma_20'] < indicators['moving_averages']['sma_50'] < 
              indicators['moving_averages']['sma_200']):
            signals['moving_averages'] = "sell"
            
        # Volume
        if indicators['volume']['current'] > indicators['volume']['sma'] * 1.5:
            signals['volume'] = "high"
        elif indicators['volume']['current'] < indicators['volume']['sma'] * 0.5:
            signals['volume'] = "low"
            
        return signals
    
    def _analyze_trend(self, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa a tendência atual do token"""
        trend = {
            "direction": "neutral",
            "strength": "weak",
            "timeframe": "short_term"
        }
        
        # Determina direção
        if (indicators['moving_averages']['sma_20'] > indicators['moving_averages']['sma_50'] and
            indicators['rsi'] > 50):
            trend['direction'] = "uptrend"
        elif (indicators['moving_averages']['sma_20'] < indicators['moving_averages']['sma_50'] and
              indicators['rsi'] < 50):
            trend['direction'] = "downtrend"
            
        # Determina força
        if abs(indicators['macd']['diff']) > 0.5:
            trend['strength'] = "strong"
        elif abs(indicators['macd']['diff']) > 0.2:
            trend['strength'] = "moderate"
            
        return trend
    
    def _find_support_resistance(self, df: pd.DataFrame) -> Dict[str, List[float]]:
        """Encontra níveis de suporte e resistência"""
        levels = {
            "support": [],
            "resistance": []
        }
        
        # Implementação simplificada usando pivots
        pivot = (df['high'].iloc[-1] + df['low'].iloc[-1] + df['close'].iloc[-1]) / 3
        r1 = 2 * pivot - df['low'].iloc[-1]
        s1 = 2 * pivot - df['high'].iloc[-1]
        
        current_price = df['close'].iloc[-1]
        
        if current_price > pivot:
            levels['support'].append(s1)
            levels['resistance'].append(r1)
        else:
            levels['support'].append(s1)
            levels['resistance'].append(pivot)
            
        return levels

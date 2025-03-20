"""
Agente de análise técnica para tokens usando APIs gratuitas.
"""
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from loguru import logger

from src.core.base_agent import BaseAgent
from src.integrations.cryptocompare import cryptocompare_client
from src.integrations.coingecko import coingecko_client
from src.utils.data_fetcher import DataFetcher

class TechnicalAgent(BaseAgent):
    """Agente para análise técnica de tokens usando APIs gratuitas"""
    
    def __init__(self):
        super().__init__()
        self.description = "Agente especializado em análise técnica de tokens"
        self.data_fetcher = DataFetcher()
        
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
            logger.info(f"Obtendo dados históricos para {token_data['symbol']}")
            ohlcv = await self._fetch_historical_data(
                token_data['symbol'],
                token_data['timeframe']
            )
            
            if ohlcv.empty:
                return {"error": f"Não foi possível obter dados históricos para {token_data['symbol']}"}
            
            # Calcula indicadores técnicos
            logger.info("Calculando indicadores técnicos")
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
            logger.error(f"Erro na análise técnica: {str(e)}")
            return {"error": str(e)}
    
    async def _fetch_historical_data(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """
        Obtém dados históricos do token usando múltiplas fontes.
        
        Args:
            symbol: Símbolo do token (ex: BTC)
            timeframe: Período de tempo (ex: 1d, 4h, 1h)
            
        Returns:
            DataFrame com dados OHLCV
        """
        try:
            # Primeiro tenta usar CryptoCompare (tem API key no .env)
            data = await cryptocompare_client.get_historical_ohlcv(symbol, timeframe, limit=100)
            
            if not data or len(data) < 30:
                # Se falhar, tenta usar CoinGecko (gratuito com rate limiting)
                logger.info("Alternando para CoinGecko")
                data = await coingecko_client.get_token_history(symbol, days=100)
            
            if not data or len(data) < 30:
                logger.error(f"Não foi possível obter dados históricos para {symbol}")
                return pd.DataFrame()
                
            # Converte para DataFrame
            df = pd.DataFrame(data)
            
            # Padroniza as colunas
            if 'time' in df.columns:
                df.rename(columns={'time': 'timestamp'}, inplace=True)
            if 'open' not in df.columns and 'prices' in df.columns:
                # Adaptação para formato do CoinGecko
                df['open'] = df['prices']
                df['high'] = df['prices'] * 1.001  # Estimativa simples
                df['low'] = df['prices'] * 0.999   # Estimativa simples
                df['close'] = df['prices']
                df['volume'] = df.get('total_volumes', 0)
                
            # Garante que as colunas estejam presentes
            required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            for col in required_cols:
                if col not in df.columns:
                    if col == 'volume':
                        df[col] = 0
                    else:
                        logger.error(f"Coluna {col} não encontrada nos dados")
                        return pd.DataFrame()
            
            # Ordena por timestamp
            df.sort_values('timestamp', inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Erro ao obter dados históricos: {str(e)}")
            return pd.DataFrame()
    
    def _calculate_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calcula indicadores técnicos a partir dos dados OHLCV.
        
        Args:
            df: DataFrame com dados OHLCV
            
        Returns:
            Dicionário com indicadores calculados
        """
        results = {}
        
        try:
            # RSI
            close_prices = df['close'].values
            delta = np.diff(close_prices)
            gain = np.where(delta > 0, delta, 0)
            loss = np.where(delta < 0, -delta, 0)
            
            avg_gain = np.mean(gain[-14:])
            avg_loss = np.mean(loss[-14:])
            
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
                
            results['rsi'] = {
                'value': round(rsi, 2),
                'signal': 'oversold' if rsi < 30 else 'overbought' if rsi > 70 else 'neutral'
            }
            
            # Médias móveis
            sma_20 = df['close'].rolling(window=20).mean().iloc[-1]
            sma_50 = df['close'].rolling(window=50).mean().iloc[-1]
            sma_200 = df['close'].rolling(window=50).mean().iloc[-1]  # Usamos 50 porque pode não ter 200 dados
            
            current_price = df['close'].iloc[-1]
            
            results['moving_averages'] = {
                'sma_20': round(sma_20, 2),
                'sma_50': round(sma_50, 2),
                'sma_200': round(sma_200, 2),
                'price': round(current_price, 2),
                'signal': 'bullish' if current_price > sma_20 > sma_50 else 'bearish' if current_price < sma_20 < sma_50 else 'neutral'
            }
            
            # MACD - Versão simplificada
            ema_12 = df['close'].ewm(span=12).mean()
            ema_26 = df['close'].ewm(span=26).mean()
            macd_line = ema_12 - ema_26
            signal_line = macd_line.ewm(span=9).mean()
            
            macd_current = macd_line.iloc[-1]
            signal_current = signal_line.iloc[-1]
            
            results['macd'] = {
                'value': round(macd_current, 2),
                'signal_line': round(signal_current, 2),
                'histogram': round(macd_current - signal_current, 2),
                'signal': 'bullish' if macd_current > signal_current else 'bearish'
            }
            
            # Bandas de Bollinger
            sma_20 = df['close'].rolling(window=20).mean()
            std_20 = df['close'].rolling(window=20).std()
            upper_band = sma_20 + (std_20 * 2)
            lower_band = sma_20 - (std_20 * 2)
            
            results['bollinger_bands'] = {
                'upper': round(upper_band.iloc[-1], 2),
                'middle': round(sma_20.iloc[-1], 2),
                'lower': round(lower_band.iloc[-1], 2),
                'current_price': round(current_price, 2),
                'signal': 'oversold' if current_price <= lower_band.iloc[-1] else 'overbought' if current_price >= upper_band.iloc[-1] else 'neutral'
            }
            
            # Volume médio
            avg_volume = df['volume'].mean()
            current_volume = df['volume'].iloc[-1]
            
            results['volume'] = {
                'current': int(current_volume),
                'average': int(avg_volume),
                'ratio': round(current_volume / avg_volume if avg_volume > 0 else 0, 2),
                'signal': 'high' if current_volume > avg_volume * 1.5 else 'low' if current_volume < avg_volume * 0.5 else 'normal'
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Erro ao calcular indicadores: {str(e)}")
            return {"error": str(e)}
    
    def _generate_signals(self, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera sinais de compra/venda com base nos indicadores.
        
        Args:
            indicators: Dicionário com indicadores técnicos
            
        Returns:
            Dicionário com sinais gerados
        """
        signals = {}
        
        try:
            # Sinal do RSI
            rsi = indicators.get('rsi', {})
            rsi_value = rsi.get('value', 50)
            
            signals['rsi'] = {
                'signal': 'buy' if rsi_value < 30 else 'sell' if rsi_value > 70 else 'neutral',
                'strength': 'strong' if rsi_value < 20 or rsi_value > 80 else 'moderate'
            }
            
            # Sinal das médias móveis
            ma = indicators.get('moving_averages', {})
            price = ma.get('price', 0)
            sma_20 = ma.get('sma_20', 0)
            sma_50 = ma.get('sma_50', 0)
            
            ma_signal = 'neutral'
            if price > sma_20 > sma_50:
                ma_signal = 'buy'
            elif price < sma_20 < sma_50:
                ma_signal = 'sell'
            elif price > sma_20 and price < sma_50:
                ma_signal = 'neutral_bearish'
            elif price < sma_20 and price > sma_50:
                ma_signal = 'neutral_bullish'
                
            signals['moving_averages'] = {
                'signal': ma_signal,
                'strength': 'strong' if abs(price - sma_50) / sma_50 > 0.05 else 'moderate'
            }
            
            # Sinal do MACD
            macd = indicators.get('macd', {})
            macd_value = macd.get('value', 0)
            signal_value = macd.get('signal_line', 0)
            
            signals['macd'] = {
                'signal': 'buy' if macd_value > signal_value else 'sell',
                'strength': 'strong' if abs(macd_value - signal_value) > 1 else 'moderate'
            }
            
            # Sinal das Bandas de Bollinger
            bb = indicators.get('bollinger_bands', {})
            bb_upper = bb.get('upper', 0)
            bb_lower = bb.get('lower', 0)
            bb_price = bb.get('current_price', 0)
            
            signals['bollinger_bands'] = {
                'signal': 'buy' if bb_price <= bb_lower else 'sell' if bb_price >= bb_upper else 'neutral',
                'strength': 'strong' if bb_price <= bb_lower * 0.98 or bb_price >= bb_upper * 1.02 else 'moderate'
            }
            
            # Sinal de volume
            vol = indicators.get('volume', {})
            vol_ratio = vol.get('ratio', 1)
            
            signals['volume'] = {
                'signal': 'bullish' if vol_ratio > 1.5 else 'bearish' if vol_ratio < 0.5 else 'neutral',
                'strength': 'strong' if vol_ratio > 2 or vol_ratio < 0.3 else 'moderate'
            }
            
            # Sinal combinado
            buy_signals = sum(1 for s in signals.values() if s.get('signal') in ['buy', 'bullish'])
            sell_signals = sum(1 for s in signals.values() if s.get('signal') in ['sell', 'bearish'])
            
            overall_signal = 'neutral'
            if buy_signals >= 3:
                overall_signal = 'strong_buy'
            elif buy_signals >= 2:
                overall_signal = 'buy'
            elif sell_signals >= 3:
                overall_signal = 'strong_sell'
            elif sell_signals >= 2:
                overall_signal = 'sell'
                
            signals['overall'] = {
                'signal': overall_signal,
                'buy_signals': buy_signals,
                'sell_signals': sell_signals,
                'neutral_signals': len(signals) - buy_signals - sell_signals
            }
            
            return signals
            
        except Exception as e:
            logger.error(f"Erro ao gerar sinais: {str(e)}")
            return {"error": str(e)}
    
    def _analyze_trend(self, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa a tendência atual do preço.
        
        Args:
            indicators: Dicionário com indicadores técnicos
            
        Returns:
            Análise de tendência
        """
        try:
            ma = indicators.get('moving_averages', {})
            price = ma.get('price', 0)
            sma_20 = ma.get('sma_20', 0)
            sma_50 = ma.get('sma_50', 0)
            
            rsi = indicators.get('rsi', {}).get('value', 50)
            macd_value = indicators.get('macd', {}).get('value', 0)
            
            # Determina a tendência
            trend = 'neutral'
            if price > sma_20 > sma_50 and rsi > 50 and macd_value > 0:
                trend = 'strong_uptrend'
            elif price > sma_20 and rsi > 50:
                trend = 'uptrend'
            elif price < sma_20 < sma_50 and rsi < 50 and macd_value < 0:
                trend = 'strong_downtrend'
            elif price < sma_20 and rsi < 50:
                trend = 'downtrend'
            
            # Calcula força da tendência
            strength = 'weak'
            if abs(price - sma_50) / sma_50 > 0.1:
                strength = 'strong'
            elif abs(price - sma_50) / sma_50 > 0.05:
                strength = 'moderate'
                
            # Calcula estágio da tendência
            stage = 'unknown'
            if trend in ['uptrend', 'strong_uptrend']:
                if rsi > 70:
                    stage = 'late'
                elif rsi > 50:
                    stage = 'middle'
                else:
                    stage = 'early'
            elif trend in ['downtrend', 'strong_downtrend']:
                if rsi < 30:
                    stage = 'late'
                elif rsi < 50:
                    stage = 'middle'
                else:
                    stage = 'early'
                    
            return {
                'trend': trend,
                'strength': strength,
                'stage': stage,
                'recommendation': self._get_recommendation(trend, stage, strength)
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar tendência: {str(e)}")
            return {"error": str(e)}
    
    def _get_recommendation(self, trend: str, stage: str, strength: str) -> str:
        """Gera uma recomendação baseada na análise de tendência"""
        if trend == 'strong_uptrend':
            if stage == 'early':
                return 'strong_buy'
            elif stage == 'middle':
                return 'buy'
            else:
                return 'hold'
        elif trend == 'uptrend':
            if stage == 'early':
                return 'buy'
            elif stage == 'middle':
                return 'buy'
            else:
                return 'hold'
        elif trend == 'strong_downtrend':
            if stage == 'early':
                return 'strong_sell'
            elif stage == 'middle':
                return 'sell'
            else:
                return 'hold'
        elif trend == 'downtrend':
            if stage == 'early':
                return 'sell'
            elif stage == 'middle':
                return 'sell'
            else:
                return 'hold'
        return 'neutral'
    
    def _find_support_resistance(self, df: pd.DataFrame) -> Dict[str, List[float]]:
        """
        Identifica níveis de suporte e resistência.
        
        Args:
            df: DataFrame com dados OHLCV
            
        Returns:
            Dicionário com níveis de suporte e resistência
        """
        try:
            # Versão simplificada para identificar suportes e resistências
            highs = df['high'].values
            lows = df['low'].values
            
            # Picos de alta (possíveis resistências)
            resistance_levels = []
            for i in range(2, len(highs) - 2):
                if highs[i] > highs[i-1] and highs[i] > highs[i-2] and highs[i] > highs[i+1] and highs[i] > highs[i+2]:
                    resistance_levels.append(round(highs[i], 2))
            
            # Picos de baixa (possíveis suportes)
            support_levels = []
            for i in range(2, len(lows) - 2):
                if lows[i] < lows[i-1] and lows[i] < lows[i-2] and lows[i] < lows[i+1] and lows[i] < lows[i+2]:
                    support_levels.append(round(lows[i], 2))
            
            # Limita a 5 níveis de cada
            resistance_levels = sorted(set(resistance_levels), reverse=True)[:5]
            support_levels = sorted(set(support_levels))[:5]
            
            return {
                'resistance': resistance_levels,
                'support': support_levels
            }
            
        except Exception as e:
            logger.error(f"Erro ao encontrar suporte/resistência: {str(e)}")
            return {"resistance": [], "support": []}

# Instância global do agente técnico
technical_agent = TechnicalAgent() 
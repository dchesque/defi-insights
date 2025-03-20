"""
Agente de análise técnica para tokens usando APIs gratuitas.
"""
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from loguru import logger

from ..core.base_agent import BaseAgent
from ..integrations.cryptocompare import cryptocompare_client
from ..integrations.coingecko import coingecko_client

class TechnicalAgent(BaseAgent):
    """Agente para análise técnica de tokens usando APIs gratuitas"""
    
    def __init__(self):
        super().__init__()
        self.description = "Agente especializado em análise técnica de tokens"
        # Adicionar nome para o agent_manager
        self.name = "TechnicalAgent"
        # Remover a dependência do DataFetcher que foi descontinuado
        # self.data_fetcher = DataFetcher()
        
    async def validate_input(self, token_data: Dict[str, Any]) -> bool:
        """
        Valida os dados de entrada do token.
        
        Args:
            token_data: Dados do token para validação
            
        Returns:
            bool: True se os dados são válidos, False caso contrário
        """
        if not token_data:
            logger.error("Dados de entrada vazios")
            return False
            
        required_fields = ['symbol', 'timeframe']
        if not all(field in token_data for field in required_fields):
            logger.error(f"Campos obrigatórios não fornecidos: {required_fields}")
            return False
            
        return True
    
    async def analyze(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza análise técnica do token.
        
        Args:
            token_data: Dados do token para análise
            
        Returns:
            Dict[str, Any]: Resultado da análise técnica
        """
        try:
            if not await self.validate_input(token_data):
                logger.error("Dados de entrada inválidos")
                return {"error": "Dados de entrada inválidos"}
                
            symbol = token_data['symbol']
            timeframe = token_data['timeframe']
            
            # Verificar cache
            cache_key = f"{symbol.upper()}_{timeframe}"
            cached_result = await self.get_cached_result(cache_key)
            if cached_result:
                logger.info(f"Retornando resultado em cache para {symbol} ({timeframe})")
                return cached_result
            
            # Obtém dados históricos
            logger.info(f"Obtendo dados históricos para {symbol}")
            ohlcv = await self._fetch_historical_data(symbol, timeframe)
            
            if ohlcv.empty:
                return {"error": f"Não foi possível obter dados históricos para {symbol}"}
            
            # Calcula indicadores técnicos
            logger.info("Calculando indicadores técnicos")
            indicators = self._calculate_indicators(ohlcv)
            
            # Gera sinais
            signals = self._generate_signals(indicators)
            
            # Análise de tendência
            trend_analysis = self._analyze_trend(indicators)
            
            # Níveis de suporte e resistência
            levels = self._find_support_resistance(ohlcv)
            
            # Compila o resultado
            result = {
                "symbol": symbol,
                "timeframe": timeframe,
                "indicators": indicators,
                "signals": signals,
                "trend_analysis": trend_analysis,
                "support_resistance": levels,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Salva no cache
            await self.save_to_cache(cache_key, result)
            
            return result
            
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
            data = await cryptocompare_client.get_historical_data(symbol, timeframe=timeframe, limit=100)
            
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
        try:
            # Cálculo manual de indicadores sem depender de bibliotecas externas
            results = {}
            
            # RSI - Implementação simples
            delta = df['close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            
            avg_gain = gain.rolling(window=14).mean()
            avg_loss = loss.rolling(window=14).mean()
            
            rs = avg_gain / avg_loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # Médias Móveis Simples
            df['sma_20'] = df['close'].rolling(window=20).mean()
            df['sma_50'] = df['close'].rolling(window=50).mean()
            df['sma_200'] = df['close'].rolling(window=200).mean()
            
            # MACD - Implementação simplificada
            df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
            df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
            df['macd'] = df['ema_12'] - df['ema_26']
            df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
            df['macd_diff'] = df['macd'] - df['macd_signal']
            
            # Bollinger Bands
            df['bb_mid'] = df['close'].rolling(window=20).mean()
            df['bb_std'] = df['close'].rolling(window=20).std()
            df['bb_high'] = df['bb_mid'] + 2 * df['bb_std']
            df['bb_low'] = df['bb_mid'] - 2 * df['bb_std']
            
            # Volume SMA
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            
            # Retornar última linha de indicadores para o estado atual
            last_row = df.iloc[-1].replace([np.inf, -np.inf], np.nan).fillna(0)
            
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
            logger.error(f"Erro ao calcular indicadores: {str(e)}")
            return {
                "rsi": 50,
                "macd": {"macd": 0, "signal": 0, "diff": 0},
                "bollinger_bands": {"high": 0, "low": 0, "middle": 0},
                "moving_averages": {"sma_20": 0, "sma_50": 0, "sma_200": 0},
                "volume": {"current": 0, "sma": 0}
            }
    
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

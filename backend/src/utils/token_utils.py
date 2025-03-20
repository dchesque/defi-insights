"""
Utilitários para manipulação e normalização de dados de tokens cripto.
"""
import re
import json
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
import pandas as pd
import numpy as np

# Mapeamento de símbolos para identificadores padronizados
SYMBOL_MAPPINGS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "USDT": "tether",
    "BNB": "binancecoin",
    "SOL": "solana",
    "XRP": "ripple",
    "ADA": "cardano",
    "DOGE": "dogecoin",
    "MATIC": "polygon",
    "DOT": "polkadot",
    # Adicione mais mapeamentos conforme necessário
}

# Cadeias de blockchain comuns
COMMON_CHAINS = {
    "eth": "Ethereum",
    "bsc": "Binance Smart Chain",
    "polygon": "Polygon",
    "sol": "Solana",
    "avax": "Avalanche",
    "ftm": "Fantom",
    "arb": "Arbitrum",
    "op": "Optimism",
    "base": "Base"
}

def normalize_symbol(symbol: str) -> str:
    """
    Normaliza o símbolo de um token para um formato padrão.
    
    Args:
        symbol: Símbolo a ser normalizado
        
    Returns:
        Símbolo normalizado
    """
    # Remove caracteres especiais
    symbol = re.sub(r'[^\w\s]', '', symbol)
    
    # Converte para maiúsculas
    symbol = symbol.upper()
    
    # Remove espaços
    symbol = symbol.strip()
    
    return symbol

def symbol_to_id(symbol: str) -> str:
    """
    Converte um símbolo de token para ID usado em APIs como CoinGecko.
    
    Args:
        symbol: O símbolo do token (ex: BTC)
        
    Returns:
        ID do token para uso em APIs (ex: bitcoin)
    """
    normalized = normalize_symbol(symbol)
    
    # Retorna direto do mapeamento se existir
    if normalized in SYMBOL_MAPPINGS:
        return SYMBOL_MAPPINGS[normalized]
    
    # Caso contrário, retorna o símbolo em minúsculas
    return normalized.lower()

def parse_contract_address(address: str) -> Dict[str, str]:
    """
    Analisa um endereço de contrato e detecta a chain.
    
    Args:
        address: O endereço do contrato
        
    Returns:
        Dicionário com o endereço limpo e a chain detectada
    """
    if not address:
        raise ValueError("Endereço de contrato não pode ser vazio")
    
    # Remove espaços e prefixo 0x se necessário
    clean_address = address.strip()
    
    # Detecta se há um prefixo de chain (ex: eth:0x...)
    chain = "eth"  # padrão Ethereum
    if ":" in clean_address:
        parts = clean_address.split(":")
        if len(parts) == 2:
            chain_prefix, contract = parts
            if chain_prefix.lower() in COMMON_CHAINS:
                chain = chain_prefix.lower()
                clean_address = contract
    
    # Adiciona 0x se não houver para endereços EVM
    if chain in ["eth", "bsc", "polygon", "avax", "ftm", "arb", "op", "base"]:
        if not clean_address.startswith("0x"):
            clean_address = f"0x{clean_address}"
    
    return {
        "address": clean_address,
        "chain": chain
    }

def format_price(price: float, currency: str = "USD") -> str:
    """
    Formata um preço com o símbolo da moeda.
    
    Args:
        price: Valor do preço
        currency: Código da moeda (padrão: USD)
        
    Returns:
        Preço formatado
    """
    if price is None:
        return "N/A"
    
    # Define o símbolo da moeda
    symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "BRL": "R$"
    }
    
    symbol = symbols.get(currency, currency)
    
    # Formata com base no valor
    if price < 0.01:
        return f"{symbol}{price:.6f}"
    elif price < 1:
        return f"{symbol}{price:.4f}"
    elif price < 10:
        return f"{symbol}{price:.2f}"
    else:
        return f"{symbol}{int(price):,}"

def format_large_number(number: float, decimals: int = 2) -> str:
    """
    Formata números grandes com sufixos K, M, B, T.
    
    Args:
        number: O número a ser formatado
        decimals: Número de casas decimais
        
    Returns:
        Número formatado com sufixo apropriado
    """
    if number is None:
        return "N/A"
    
    if number == 0:
        return "0"
    
    suffix = ""
    
    if abs(number) >= 1_000_000_000_000:
        number /= 1_000_000_000_000
        suffix = "T"
    elif abs(number) >= 1_000_000_000:
        number /= 1_000_000_000
        suffix = "B"
    elif abs(number) >= 1_000_000:
        number /= 1_000_000
        suffix = "M"
    elif abs(number) >= 1_000:
        number /= 1_000
        suffix = "K"
    
    format_str = f"{{:.{decimals}f}}{{suffix}}"
    return format_str.format(number, suffix=suffix)

def format_percent(value: float, include_sign: bool = True) -> str:
    """
    Formata um valor percentual.
    
    Args:
        value: O valor percentual
        include_sign: Se deve incluir sinal +/- 
        
    Returns:
        Percentual formatado (ex: +12.34%)
    """
    if value is None:
        return "N/A"
    
    sign = ""
    if include_sign and value > 0:
        sign = "+"
    
    return f"{sign}{value:.2f}%"

def timeframe_to_seconds(timeframe: str) -> int:
    """
    Converte um timeframe (1m, 1h, 1d) para segundos.
    
    Args:
        timeframe: O timeframe (ex: 1m, 5m, 15m, 1h, 4h, 1d, 1w)
        
    Returns:
        O número de segundos
    """
    if not timeframe:
        raise ValueError("Timeframe não pode ser vazio")
    
    # Regex para extrair número e unidade
    match = re.match(r'(\d+)([mhdwMy])', timeframe)
    if not match:
        raise ValueError(f"Formato de timeframe inválido: {timeframe}")
    
    value, unit = match.groups()
    value = int(value)
    
    # Converter para segundos
    if unit == 'm':  # minutos
        return value * 60
    elif unit == 'h':  # horas
        return value * 60 * 60
    elif unit == 'd':  # dias
        return value * 24 * 60 * 60
    elif unit == 'w':  # semanas
        return value * 7 * 24 * 60 * 60
    elif unit == 'M':  # meses (aproximado)
        return value * 30 * 24 * 60 * 60
    elif unit == 'y':  # anos (aproximado)
        return value * 365 * 24 * 60 * 60
    else:
        raise ValueError(f"Unidade de timeframe desconhecida: {unit}")

def generate_token_id(symbol: str, user_id: str) -> str:
    """
    Gera um ID para uma análise de token.
    
    Args:
        symbol: O símbolo do token
        user_id: ID do usuário
        
    Returns:
        ID único para a análise
    """
    timestamp = int(datetime.now().timestamp())
    normalized_symbol = normalize_symbol(symbol)
    return f"{normalized_symbol}_{user_id}_{timestamp}"

def parse_token_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analisa e normaliza dados de token de diferentes fontes.
    
    Args:
        data: Dados brutos do token
        
    Returns:
        Dados normalizados do token
    """
    result = {}
    
    # Extrair campos comuns e normalizar
    if "symbol" in data:
        result["symbol"] = normalize_symbol(data["symbol"])
    
    if "name" in data:
        result["name"] = data["name"]
    
    if "price" in data:
        result["price"] = float(data["price"])
    elif "current_price" in data:
        result["price"] = float(data["current_price"])
    
    if "market_cap" in data:
        result["market_cap"] = float(data["market_cap"])
    
    if "volume" in data or "total_volume" in data:
        result["volume_24h"] = float(data.get("volume") or data.get("total_volume", 0))
    
    # Normalizar timestamp
    if "timestamp" in data:
        if isinstance(data["timestamp"], (int, float)):
            result["timestamp"] = datetime.fromtimestamp(data["timestamp"])
        elif isinstance(data["timestamp"], str):
            try:
                result["timestamp"] = datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
            except ValueError:
                # Fallback para timestamp atual
                result["timestamp"] = datetime.now()
    else:
        result["timestamp"] = datetime.now()
    
    return result

def serialize_datetime(obj):
    """
    Função auxiliar para serializar objetos datetime para JSON.
    
    Args:
        obj: O objeto a ser serializado
        
    Returns:
        Representação serializada do objeto
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Tipo não serializável: {type(obj)}")

def to_json(data: Any) -> str:
    """
    Converte dados para JSON com formato amigável.
    
    Args:
        data: Dados a serem convertidos
        
    Returns:
        String JSON formatada
    """
    class CustomEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (datetime, pd.Timestamp)):
                return obj.isoformat()
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif pd.isna(obj):
                return None
            return super().default(obj)
    
    return json.dumps(data, indent=2, cls=CustomEncoder, ensure_ascii=False)

def from_json(json_str: str) -> Any:
    """
    Converte string JSON para objeto Python.
    
    Args:
        json_str: A string JSON
        
    Returns:
        Objeto Python
    """
    return json.loads(json_str)

def calculate_rsi(prices: List[float], period: int = 14) -> float:
    """
    Calcula o RSI (Relative Strength Index) para uma série de preços.
    
    Args:
        prices: Lista de preços em ordem cronológica
        period: Período para o cálculo (padrão: 14)
        
    Returns:
        Valor do RSI
    """
    if len(prices) < period + 1:
        return 50  # Valor neutro se não tivermos dados suficientes
    
    # Calcula as diferenças
    deltas = np.diff(prices)
    
    # Separa ganhos e perdas
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    # Calcula médias
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])
    
    if avg_loss == 0:
        return 100  # Evita divisão por zero
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi, 2)

def calculate_moving_average(prices: List[float], period: int) -> float:
    """
    Calcula a média móvel para uma série de preços.
    
    Args:
        prices: Lista de preços em ordem cronológica
        period: Período da média móvel
        
    Returns:
        Valor da média móvel
    """
    if len(prices) < period:
        return sum(prices) / len(prices)
    
    return sum(prices[-period:]) / period

def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2.0) -> Dict[str, float]:
    """
    Calcula as Bandas de Bollinger para uma série de preços.
    
    Args:
        prices: Lista de preços em ordem cronológica
        period: Período para o cálculo (padrão: 20)
        std_dev: Número de desvios padrão (padrão: 2.0)
        
    Returns:
        Dict com upper_band, middle_band e lower_band
    """
    if len(prices) < period:
        # Retorna valores aproximados se não tivermos dados suficientes
        mean = sum(prices) / len(prices)
        std = np.std(prices) if len(prices) > 1 else 0
        return {
            "upper_band": mean + std_dev * std,
            "middle_band": mean,
            "lower_band": mean - std_dev * std
        }
    
    # Obtém os últimos 'period' preços
    last_prices = prices[-period:]
    
    # Calcula a média
    middle_band = sum(last_prices) / period
    
    # Calcula o desvio padrão
    std = np.std(last_prices)
    
    # Calcula as bandas
    upper_band = middle_band + (std_dev * std)
    lower_band = middle_band - (std_dev * std)
    
    return {
        "upper_band": round(upper_band, 2),
        "middle_band": round(middle_band, 2),
        "lower_band": round(lower_band, 2)
    }

def calculate_macd(prices: List[float], fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Dict[str, float]:
    """
    Calcula o MACD (Moving Average Convergence Divergence) para uma série de preços.
    
    Args:
        prices: Lista de preços em ordem cronológica
        fast_period: Período da média rápida (padrão: 12)
        slow_period: Período da média lenta (padrão: 26)
        signal_period: Período da linha de sinal (padrão: 9)
        
    Returns:
        Dict com macd_line, signal_line e histogram
    """
    if len(prices) < slow_period + signal_period:
        return {
            "macd_line": 0,
            "signal_line": 0,
            "histogram": 0
        }
    
    # Converte para array numpy para cálculos mais eficientes
    prices_array = np.array(prices)
    
    # Calcula EMAs
    ema_fast = pd.Series(prices_array).ewm(span=fast_period, adjust=False).mean().iloc[-1]
    ema_slow = pd.Series(prices_array).ewm(span=slow_period, adjust=False).mean().iloc[-1]
    
    # Calcula linha MACD
    macd_line = ema_fast - ema_slow
    
    # Calcula histórico do MACD para a linha de sinal
    ema_fast_series = pd.Series(prices_array).ewm(span=fast_period, adjust=False).mean()
    ema_slow_series = pd.Series(prices_array).ewm(span=slow_period, adjust=False).mean()
    macd_history = ema_fast_series - ema_slow_series
    
    # Calcula linha de sinal
    signal_line = macd_history.ewm(span=signal_period, adjust=False).mean().iloc[-1]
    
    # Calcula histograma
    histogram = macd_line - signal_line
    
    return {
        "macd_line": round(macd_line, 2),
        "signal_line": round(signal_line, 2),
        "histogram": round(histogram, 2)
    }

def analyze_volume(volumes: List[float]) -> Dict[str, Any]:
    """
    Analisa o volume de negociação.
    
    Args:
        volumes: Lista de volumes em ordem cronológica
        
    Returns:
        Dict com análise de volume
    """
    if not volumes or len(volumes) < 2:
        return {
            "current": 0,
            "average": 0,
            "change": 0,
            "trend": "neutral"
        }
    
    current = volumes[-1]
    previous = volumes[-2]
    average = sum(volumes) / len(volumes)
    
    change = ((current - previous) / previous) * 100 if previous > 0 else 0
    
    # Determina a tendência do volume
    if current > average * 1.5:
        trend = "high"
    elif current < average * 0.5:
        trend = "low"
    else:
        trend = "normal"
    
    return {
        "current": int(current),
        "average": int(average),
        "change": round(change, 2),
        "trend": trend
    }

def find_support_resistance(highs: List[float], lows: List[float], periods: int = 20) -> Dict[str, List[float]]:
    """
    Identifica níveis de suporte e resistência.
    
    Args:
        highs: Lista de preços máximos em ordem cronológica
        lows: Lista de preços mínimos em ordem cronológica
        periods: Número de períodos a analisar
        
    Returns:
        Dict com listas de níveis de suporte e resistência
    """
    if len(highs) < periods or len(lows) < periods:
        return {
            "support": [],
            "resistance": []
        }
    
    # Obtém os dados do período especificado
    recent_highs = highs[-periods:]
    recent_lows = lows[-periods:]
    
    # Encontra picos de alta (possíveis resistências)
    resistance_levels = []
    for i in range(2, len(recent_highs) - 2):
        if recent_highs[i] > recent_highs[i-1] and recent_highs[i] > recent_highs[i-2] and \
           recent_highs[i] > recent_highs[i+1] and recent_highs[i] > recent_highs[i+2]:
            resistance_levels.append(round(recent_highs[i], 2))
    
    # Encontra picos de baixa (possíveis suportes)
    support_levels = []
    for i in range(2, len(recent_lows) - 2):
        if recent_lows[i] < recent_lows[i-1] and recent_lows[i] < recent_lows[i-2] and \
           recent_lows[i] < recent_lows[i+1] and recent_lows[i] < recent_lows[i+2]:
            support_levels.append(round(recent_lows[i], 2))
    
    # Remove duplicatas e ordena
    resistance_levels = sorted(set(resistance_levels), reverse=True)
    support_levels = sorted(set(support_levels))
    
    # Limita a 5 níveis
    resistance_levels = resistance_levels[:5]
    support_levels = support_levels[:5]
    
    return {
        "resistance": resistance_levels,
        "support": support_levels
    }

def generate_technical_signals(indicators: Dict[str, Any]) -> Dict[str, Any]:
    """
    Gera sinais técnicos com base nos indicadores.
    
    Args:
        indicators: Dict com indicadores técnicos
        
    Returns:
        Dict com sinais técnicos
    """
    signals = {}
    
    # RSI
    rsi = indicators.get("rsi", {}).get("value", 50)
    signals["rsi"] = {
        "signal": "buy" if rsi < 30 else "sell" if rsi > 70 else "neutral",
        "strength": "strong" if rsi < 20 or rsi > 80 else "moderate"
    }
    
    # Médias móveis
    ma = indicators.get("moving_averages", {})
    price = ma.get("price", 0)
    sma_20 = ma.get("sma_20", 0)
    sma_50 = ma.get("sma_50", 0)
    
    ma_signal = "neutral"
    if price > sma_20 > sma_50:
        ma_signal = "buy"
    elif price < sma_20 < sma_50:
        ma_signal = "sell"
    
    signals["moving_averages"] = {
        "signal": ma_signal,
        "strength": "strong" if abs(price - sma_50) / (sma_50 or 1) > 0.05 else "moderate"
    }
    
    # MACD
    macd = indicators.get("macd", {})
    macd_line = macd.get("macd_line", 0)
    signal_line = macd.get("signal_line", 0)
    
    signals["macd"] = {
        "signal": "buy" if macd_line > signal_line else "sell",
        "strength": "strong" if abs(macd_line - signal_line) > 1 else "moderate"
    }
    
    # Bandas de Bollinger
    bb = indicators.get("bollinger_bands", {})
    price = indicators.get("price", bb.get("middle_band", 0))
    upper = bb.get("upper_band", 0)
    lower = bb.get("lower_band", 0)
    
    signals["bollinger_bands"] = {
        "signal": "buy" if price <= lower else "sell" if price >= upper else "neutral",
        "strength": "strong" if price <= lower * 0.98 or price >= upper * 1.02 else "moderate"
    }
    
    # Sinal geral
    buy_signals = sum(1 for s in signals.values() if s.get("signal") == "buy")
    sell_signals = sum(1 for s in signals.values() if s.get("signal") == "sell")
    
    overall = "neutral"
    if buy_signals >= 3:
        overall = "strong_buy"
    elif buy_signals >= 2:
        overall = "buy"
    elif sell_signals >= 3:
        overall = "strong_sell"
    elif sell_signals >= 2:
        overall = "sell"
    
    signals["overall"] = {
        "signal": overall,
        "buy_signals": buy_signals,
        "sell_signals": sell_signals,
        "neutral_signals": len(signals) - buy_signals - sell_signals
    }
    
    return signals

def calculate_change_color(change: float) -> str:
    """
    Determina a cor com base na porcentagem de mudança.
    
    Args:
        change: Valor da mudança em porcentagem
        
    Returns:
        Código de cor
    """
    if change > 5:
        return "#00A300"  # Verde forte
    elif change > 0:
        return "#00CC00"  # Verde
    elif change < -5:
        return "#CC0000"  # Vermelho forte
    elif change < 0:
        return "#FF0000"  # Vermelho
    else:
        return "#888888"  # Cinza

def safe_divide(a: float, b: float, default: float = 0) -> float:
    """
    Realiza divisão segura evitando divisão por zero.
    
    Args:
        a: Numerador
        b: Denominador
        default: Valor padrão caso o denominador seja zero
        
    Returns:
        Resultado da divisão ou valor padrão
    """
    return a / b if b != 0 else default 
import pandas as pd


def ema(series, span):
    alpha = 2 / (span + 1)
    result = [series[0]]

    for i in range(1, len(series)):
        value = alpha * series[i] + (1 - alpha) * result[i - 1]
        result.append(value)

    return result


def atr(data, span):
    high = data['High']
    low = data['Low']
    close = data['Close']

    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = true_range.rolling(window=span, min_periods=1).mean()

    return atr

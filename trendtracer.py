import pandas as pd
import numpy as np


# For other spreadsheet use this in reading csv
# , delimiter='\t', names=['Open', 'High', 'Low', 'Close', 'Volume'], header=0

# Darwinex spreadsheet
df = pd.read_csv('../Data/Darwinex/GBPUSD60.csv', header=None,
                 names=['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
df.set_index('DateTime', inplace=True)
df.drop(columns=['Date', 'Time'], inplace=True)


df = df.iloc[-500:]

# Init
conditions = [
    df.Close > df.Open,
    df.Close < df.Open
]

choices = ['Bull', 'Bear']

df['Candle'] = np.select(conditions, choices, default='Doji')
df['Swing_Low'] = df['Low'].iloc[0]
df['Swing_High'] = df['High'].iloc[0]

df['Trend'] = 'Neutral'

higher_high = None
lower_low = None

bullish_pullback_count = 0
bearish_pullback_count = 0
bullish_pullback = False
bearish_pullback = False

swing_high = df['High'].iloc[0]
swing_low = df['Low'].iloc[0]

uptrend_lowest_pullback = None
downtrend_highest_pullback = None

previous_high = df['High'].iloc[0]
previous_low = df['Low'].iloc[0]

current_trend = 'Neutral'
df.at[0, 'Trend'] = current_trend

df['Price_Status'] = None
price_status = None

print(swing_high)


# Itterating logic starts
for i, row in df.iloc[1:].iterrows():
    current_high = row['High']
    current_low = row['Low']
    candle_type = row['Candle']
    current_close = row['Close']

    # clear_output()
    # Trend rotation
    if current_close > swing_high:
        current_trend = 'Uptrend'
    elif current_close < swing_low:
        current_trend = 'Downtrend'

    df.at[i, 'Trend'] = current_trend

    if bullish_pullback or bearish_pullback:
        price_status = 'Consolidation'
    else:
        price_status = 'Extension'

    df.at[i, 'Price_Status'] = price_status
    # ================================================================================================== #

    if current_trend == 'Uptrend':
        if current_high > previous_high and not bullish_pullback:
            higher_high = current_high
        elif current_close < higher_high and candle_type == 'Bear':
            bullish_pullback_count += 1

        if bullish_pullback_count >= 2:
            bullish_pullback = True
            swing_high = higher_high
            df.at[i, 'Swing_High'] = swing_high
        else:
            bullish_pullback = False

        if bullish_pullback and current_close > swing_low:
            if current_low < previous_low:
                uptrend_lowest_pullback = current_low
        elif current_close > swing_high:
            if uptrend_lowest_pullback is not None:
                swing_low = uptrend_lowest_pullback
                df.at[i, 'Swing_Low'] = swing_low
            bullish_pullback_count = 0
            bullish_pullback = False

    elif current_trend == 'Downtrend':
        if current_low > previous_low and not bearish_pullback:
            lower_low = current_low
        elif bearish_pullback and candle_type == 'Bull':
            bearish_pullback_count += 1
        if bearish_pullback_count >= 2:
            bearish_pullback = True
            swing_low = lower_low
            df.at[i, 'Swing_Low'] = swing_low
        else:
            bearish_pullback = False

        if bearish_pullback and current_close < swing_high:
            if current_high > previous_high:
                downtrend_highest_pullback = current_high
        elif current_close < swing_low:
            if downtrend_highest_pullback is not None:
                swing_high = downtrend_highest_pullback
                df.at[i, 'Swing_High'] = swing_high
            bearish_pullback_count = 0
            bearish_pullback = False

    previous_low = current_low
    previous_high = current_high
print(df)

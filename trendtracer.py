import pandas as pd
import numpy as np
import plotly.graph_objects as go
from IPython.display import display
import matplotlib.pyplot as plt


# For other spreadsheet use this in reading csv
# , delimiter='\t', names=['Open', 'High', 'Low', 'Close', 'Volume'], header=0

# Darwinex spreadsheet
df = pd.read_csv('../Data/Darwinex/GBPUSD60.csv', header=None,
                 names=['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
df.set_index('DateTime', inplace=True)
df.drop(columns=['Date', 'Time'], inplace=True)


df = df.iloc[-300:]
# df = df.iloc[190:224]

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
df['Bar_Number'] = None

higher_high = df['High'].iloc[0]
lower_low = df['Low'].iloc[0]

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


fig = go.Figure()
bar_number = 0
# Itterating logic starts
for i, row in df.iloc[1:].iterrows():
    bar_number += 1
    df.at[i, 'Bar_Number'] = bar_number
    current_high = row['High']
    current_low = row['Low']
    candle_type = row['Candle']
    current_close = row['Close']

    # clear_output()
    # Trend rotation
    if current_close > swing_high:
        current_trend = 'Uptrend'
        bearish_pullback_count = 0
        bearish_pullback = False
    elif current_close < swing_low:
        current_trend = 'Downtrend'
        bullish_pullback_count = 0
        bullish_pullback = False
    # Finding the range in the beginning of the dataset
    elif current_trend == "Neutral":
        if swing_high is not None:
            if current_high > previous_high:
                swing_high = current_high
        if swing_low is not None:
            if current_low < previous_low:
                swing_low = current_low

    df.at[i, 'Trend'] = current_trend

    if bullish_pullback or bearish_pullback:
        price_status = 'Consolidation'
    else:
        price_status = 'Extension'

    df.at[i, 'Price_Status'] = price_status
    # ================================================================================================== #
    if current_trend == 'Uptrend':
        if current_close > swing_high:
            bullish_pullback_count = 0
            bullish_pullback = False
            if uptrend_lowest_pullback is not None:
                swing_low = uptrend_lowest_pullback
        if current_high > previous_high and current_high > swing_high and not bullish_pullback:
            swing_high = current_high
        if current_close < swing_high and candle_type == 'Bear':
            bullish_pullback_count += 1

        if bullish_pullback_count >= 2:
            bullish_pullback = True
        else:
            bullish_pullback = False

        if bullish_pullback and current_close > swing_low:
            if current_low < previous_low:
                uptrend_lowest_pullback = current_low

    elif current_trend == 'Downtrend':
        if current_close < swing_low:
            if downtrend_highest_pullback is not None:
                swing_high = downtrend_highest_pullback
            bearish_pullback_count = 0
            bearish_pullback = False
        if current_low < previous_low and current_low < swing_low and not bearish_pullback:
            swing_low = current_low
        if current_close > swing_low and candle_type == 'Bull':
            bearish_pullback_count += 1
        if bearish_pullback_count >= 2:
            bearish_pullback = True

        if bearish_pullback and current_close < swing_high:
            if current_high > previous_high:
                downtrend_highest_pullback = current_high

    df.at[i, 'Swing_High'] = swing_high
    df.at[i, 'Swing_Low'] = swing_low
    previous_low = current_low
    previous_high = current_high

    # ============================ITTERATION PLOT ======================================

    # custom_text = df['Bar_Number'].astype(str) + '<br>' + 'Swing High: ' + df['Swing_High'].astype(
    #     str) + '<br>' + 'Swing Low: ' + df['Swing_Low'].astype(str)
    # fig.add_trace(go.Candlestick(x=[i],
    #                              open=[row['Open']],
    #                              high=[row['High']],
    #                              low=[row['Low']],
    #                              close=[row['Close']],
    #                              hoverinfo='x+y+text',
    #                              text=custom_text,
    #                              name=f'Candle {i}'))

    # uptrend_markers = df[df['Trend'] == 'Uptrend']
    # downtrend_markers = df[df['Trend'] == 'Downtrend']

    # fig.add_trace(go.Scatter(x=uptrend_markers.index, y=uptrend_markers['Low'] - 0.001 * uptrend_markers['Low'],
    #               mode='markers', name='Uptrend', marker=dict(symbol='triangle-up', color='blue', size=8)))
    # fig.add_trace(go.Scatter(x=downtrend_markers.index, y=downtrend_markers['High'] + 0.001 * downtrend_markers['High'],
    #               mode='markers', name='Downtrend', marker=dict(symbol='triangle-down', color='orange', size=8)))

    # fig.update_layout(
    #     template='plotly_dark',
    #     xaxis=dict(showgrid=False),
    #     yaxis=dict(showgrid=False),
    # )
    # display(fig.show())


# ========================= PLOT ALL ==================================================

    custom_text = df['Bar_Number'].astype(str) + '<br>' + 'Swing High: ' + df['Swing_High'].astype(
        str) + '<br>' + 'Swing Low: ' + df['Swing_Low'].astype(str)
    fig = go.Figure(data=[go.Candlestick(x=df.index,
                                         open=df['Open'],
                                         high=df['High'],
                                         low=df['Low'],
                                         close=df['Close'],
                                         hoverinfo='x+y+text',
                                         text=custom_text,
                                         name='Candlestick')])

# Add trend markers (prioritize uptrend over downtrend)
uptrend_markers = df[df['Trend'] == 'Uptrend']
downtrend_markers = df[df['Trend'] == 'Downtrend']

fig.add_trace(go.Scatter(x=uptrend_markers.index, y=uptrend_markers['Low'] - 0.001 * uptrend_markers['Low'],
              mode='markers', name='Uptrend', marker=dict(symbol='triangle-up', color='blue', size=8)))
fig.add_trace(go.Scatter(x=downtrend_markers.index, y=downtrend_markers['High'] + 0.001 * downtrend_markers['High'],
              mode='markers', name='Downtrend', marker=dict(symbol='triangle-down', color='orange', size=8)))

# Update the layout for a clearer view
fig.update_layout(title='Candlestick Chart with Swing Highs and Lows',
                  height=600,
                  template='plotly_dark',
                  xaxis=dict(type='category', nticks=20, showgrid=False),
                  xaxis_rangeslider_visible=False)

# Show the figure
fig.show()
import plotly.graph_objects as go
import pandas as pd
import numpy as np

df = pd.read_csv('../Data/Darwinex/USDJPY60.csv', header=None,
                 names=['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
df.set_index('DateTime', inplace=True)
df.drop(columns=['Date', 'Time'], inplace=True)


# Initialize variables to track the trend and potential swing points
current_trend = 'undetermined'
swing_high = float('-inf')
swing_low = float('inf')
potential_swing_high = 0
potential_swing_low = float('inf')
pullback_count = 0

# Columns for the official Swing High and Swing Low values
df['Swing High Value'] = np.nan
df['Swing Low Value'] = np.nan

for i in range(1, len(df)):
    # Determine the current trend and track potential swing points
    if current_trend == 'undetermined' or current_trend == 'uptrend':
        if df['Close'].iloc[i] > df['Close'].iloc[i-1]:
            # Update potential swing high during an uptrend or undetermined trend
            potential_swing_high = max(
                potential_swing_high, df['High'].iloc[i])
            pullback_count = 0  # Reset pullback counter
        else:
            pullback_count += 1
            # Track the lowest point during the pullback
            potential_swing_low = min(potential_swing_low, df['Low'].iloc[i])

            if pullback_count >= 2:
                # Confirm the swing high once a pullback is detected
                if potential_swing_high != 0:
                    df.loc[df.index[i-2],
                           'Swing High Value'] = potential_swing_high
                    swing_high = potential_swing_high
                    potential_swing_high = 0  # Reset potential swing high

                # Check for trend continuation or change after the pullback
                if df['Close'].iloc[i] > swing_high:
                    current_trend = 'uptrend'
                    df.loc[df.index[i-2], 'Swing Low Value'] = potential_swing_low
                    swing_low = potential_swing_low
                    # Reset potential swing low
                    potential_swing_low = float('inf')
                else:
                    current_trend = 'downtrend'

    elif current_trend == 'downtrend':
        if df['Close'].iloc[i] < df['Close'].iloc[i-1]:
            # Update potential swing low during a downtrend
            potential_swing_low = min(potential_swing_low, df['Low'].iloc[i])
            pullback_count = 0  # Reset pullback counter
        else:
            pullback_count += 1
            # Track the highest point during the pullback
            potential_swing_high = max(
                potential_swing_high, df['High'].iloc[i])

            if pullback_count >= 2:
                # Confirm the swing low once a pullback is detected
                if potential_swing_low != float('inf'):
                    df.loc[df.index[i-2], 'Swing Low Value'] = potential_swing_low
                    swing_low = potential_swing_low
                    # Reset potential swing low
                    potential_swing_low = float('inf')

                # Check for trend continuation or change after the pullback
                if df['Close'].iloc[i] < swing_low:
                    current_trend = 'downtrend'
                    df.loc[df.index[i-2],
                           'Swing High Value'] = potential_swing_high
                    swing_high = potential_swing_high
                    potential_swing_high = 0  # Reset potential swing high
                else:
                    current_trend = 'uptrend'

# Sample output
df[['High', 'Low', 'Close', 'Swing High Value', 'Swing Low Value']].tail(20)

# Creating candlestick chart
fig = go.Figure(data=[go.Candlestick(x=df.index,
                                     open=df['Open'],
                                     high=df['High'],
                                     low=df['Low'],
                                     close=df['Close'])])

# Adding Swing Highs and Lows as scatter plots
fig.add_trace(go.Scatter(x=df.index, y=df['Swing High Value'],
              mode='markers', name='Swing High', marker=dict(color='Green', size=5)))
fig.add_trace(go.Scatter(x=df.index, y=df['Swing Low Value'],
              mode='markers', name='Swing Low', marker=dict(color='Red', size=5)))

# Updating layout for better visualization
fig.update_layout(title='USDJPY H1 with Swing Highs and Lows',
                  xaxis_title='DateTime', yaxis_title='Price', xaxis_rangeslider_visible=False)

fig.show()

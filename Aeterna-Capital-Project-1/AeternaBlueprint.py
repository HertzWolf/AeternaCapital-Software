import pandas as pd
import numpy as np
from collections import defaultdict
df = pd.read_excel("AeternaCapital.xlsx")
df.columns = df.columns.str.strip()
df['Date'] = pd.to_datetime(df['Date'])
df['Time'] = pd.to_datetime(df['Time'], format="%H:%M:%S").dt.time
df['Qty'] = pd.to_numeric(df['Qty'], errors='coerce')
df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
df['Qty']=df.apply(
    lambda row: -row['Qty'] if row['Asset'].lower() == 'Sell' else row['Qty'], axis=1
)
df['DateTime']= pd.to_datetime(
    df['Date'].astype(str) + ' ' + df['Time'].astype(str),
    format="%Y-%m-%d %H:%M:%S"
)
df = df.sort_values(by='DateTime')
starting_capital = 100000000
cash_balance = starting_capital
holdings = defaultdict(lambda: [0,0])
shorts = defaultdict(lambda: [0,0])
snapshots = []
realized_pnl = 0.0
for _, trade in df.iterrows():
    asset = trade['Asset']
    qty = trade['Qty']
    price = trade['Price']
    side = trade['Buy / Sell'].strip().lower()
    dt = trade['DateTime']
    if pd.isna(qty) or pd.isna(price):
        continue
    if side == 'buy' :
        if shorts[asset][0] < 0:
           cover_qty = min(qty, abs(shorts[asset][0]))
           pnl = (shorts[asset][1] - price) * cover_qty
           realized_pnl += pnl
           cash_balance -= cover_qty * price
           shorts[asset][0] += cover_qty
           if shorts[asset][0] == 0:
              del shorts[asset]
           qty -= cover_qty
        if qty > 0:
           old_qty, old_cost = holdings[asset]
           new_qty = old_qty + qty
           new_avg = ((old_qty * old_cost) + (qty * price)) / new_qty
           holdings[asset] = [new_qty, new_avg]
           cash_balance -= qty * price
    elif side == 'sell':
        if holdings[asset][0] > 0:
            close_qty = min(qty, holdings[asset][0])
            pnl = (price - holdings[asset][1]) * close_qty
            realized_pnl += pnl
            cash_balance += close_qty * price
            holdings[asset][0] -= close_qty
            if holdings[asset][0] == 0:
                del holdings[asset]
            sell_qty -= close_qty
        if qty > 0:
            shorts[asset][0] -= qty
            shorts[asset][1] = price
    holding_value = sum(q * p for _, (q, p) in holdings.items())
    short_exposure = sum(abs(q) * p for _, (q, p) in shorts.items())
    unrealized_pnl = (
        sum((price - cost) * q for _, (q, cost) in holdings.items()) +
        sum((entry - price) * abs(q) for _, (q,entry) in shorts.items())
    )
    total_value = cash_balance + holding_value + short_exposure

    snapshots.append ({
        'DateTime': dt,
        'Cash': round(cash_balance, 2),
        'Holdings Value': round(holding_value, 2),
        'Shorts Exposure': round(short_exposure, 2),
        'Total Portfolio Value': round(total_value, 2)
    })

snapshots_df = pd.DataFrame(snapshots)
snapshots_df.tail()

print("\n--- Open Holdings ---")
for asset, (qty, avg_cost) in holdings.items():
    print(f"{asset}: {qty} @ {avg_cost:.2f}")

print("\n--- Open Shorts ---")
for asset, (qty, entry_price) in shorts.items():
    print(f"{asset}: {qty} @ {entry_price:.2f}")

snapshots_df['LogReturn'] = np.log(snapshots_df['Total Portfolio Value'] / snapshots_df['Total Portfolio Value'].shift(1))
snapshots_df.to_excel("portfolio_lof_returns.xlsx", index=False)

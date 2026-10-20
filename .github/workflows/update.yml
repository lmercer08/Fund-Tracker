"""Fetch fund performance and write data.json. Edit FUNDS to change what's tracked."""
import json, datetime as dt
import pandas as pd
import yfinance as yf

FUNDS = {
    "MFEIX": "MFS Growth I",
    "PMYYX": "Putnam Core Equity Fund Y",
    "MGK":   "Vanguard Mega Cap Growth ETF",
    "FAGCX": "Fidelity Advisor Growth Opps I",
    "PRJZX": "PGIM Jennison Global Opportunities Z",
    "HACAX": "Harbor Capital Appreciation Instl",
    "TRBCX": "T. Rowe Price Blue Chip Growth",
    "VADDX": "Invesco Equally-Wtd S&P 500 Y",
    "GTDYX": "Invesco Emerging Markets ex-China Y",
    "PEIYX": "Putnam Large Cap Value Y",
}

def pct(now, then):
    return round((now / then - 1) * 100, 2)

def change_since(close, days):
    """% change vs. the last close on or before (latest date - days)."""
    target = close.index[-1] - pd.Timedelta(days=days)
    past = close[close.index <= target]
    return pct(close.iloc[-1], past.iloc[-1] if len(past) else close.iloc[0])

rows = []
for ticker, name in FUNDS.items():
    row = {"ticker": ticker, "name": name}
    try:
        close = yf.Ticker(ticker).history(period="13mo")["Close"].dropna()
        close.index = close.index.tz_localize(None)
        row.update(
            day=pct(close.iloc[-1], close.iloc[-2]),
            week=change_since(close, 7),
            month=change_since(close, 30),
            year=change_since(close, 365),
        )
    except Exception as e:
        row["error"] = str(e)[:80]
    rows.append(row)

out = {"updated": dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"), "funds": rows}
with open("data.json", "w") as f:
    json.dump(out, f, indent=2)
print("Wrote data.json")

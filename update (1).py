"""Fetch fund performance and write data.json.

TO ADD / REMOVE / REORDER FUNDS: edit the FUNDS list below. That's the only place to change.
Each line is:  ("TICKER", "Display name", "fund" or "etf")
 - use "fund" for mutual funds and "etf" for ETFs (this builds the right Morningstar link)
 - the website shows funds in the same order as this list (top line = top of the screen)
 - leave the name as "" to have it filled in automatically
"""
import json, datetime as dt
import pandas as pd
import yfinance as yf

FUNDS = [
    ("IVV",   "iShares Core S&P 500 ETF",              "etf"),
    ("MFEIX", "MFS Growth I",                          "fund"),
    ("PMYYX", "Putnam Core Equity Fund Y",             "fund"),
    ("MGK",   "Vanguard Mega Cap Growth ETF",          "etf"),
    ("FAGCX", "Fidelity Advisor Growth Opps I",        "fund"),
    ("PRJZX", "PGIM Jennison Global Opportunities Z",  "fund"),
    ("HACAX", "Harbor Capital Appreciation Instl",     "fund"),
    ("TRBCX", "T. Rowe Price Blue Chip Growth",        "fund"),
    ("VADDX", "Invesco Equally-Wtd S&P 500 Y",         "fund"),
    ("GTDYX", "Invesco Emerging Markets ex-China Y",   "fund"),
    ("PEIYX", "Putnam Large Cap Value Y",             "fund"),
    ("DPDFX", "Nomura Diversified Income A",             "fund"),
    ("PADZX", "PGIM Absolute Return Bond Z",           "fund"),
    ("BSIIX", "BlackRock Strategic Income Opps Instl", "fund"),
    ("RETSX", "Russell Tax-Managed US Large Cap S",    "fund"),
]

ETF_EXCHANGE = {"IVV": "arcx", "MGK": "arcx"}   # Morningstar exchange code for ETFs (default arcx)

def morningstar_url(ticker, kind):
    t = ticker.lower()
    if kind == "etf":
        return f"https://www.morningstar.com/etfs/{ETF_EXCHANGE.get(ticker, 'arcx')}/{t}/quote"
    return f"https://www.morningstar.com/funds/xnas/{t}/quote"

def pct(now, then):
    return round((now / then - 1) * 100, 2)

def change_since(close, days):
    """% change vs. the last close on or before (latest date - days)."""
    target = close.index[-1] - pd.Timedelta(days=days)
    past = close[close.index <= target]
    return pct(close.iloc[-1], past.iloc[-1] if len(past) else close.iloc[0])

rows = []
for ticker, name, kind in FUNDS:
    t = yf.Ticker(ticker)
    if not name:
        try:
            info = t.info
            name = info.get("longName") or info.get("shortName") or ticker
        except Exception:
            name = ticker
    row = {"ticker": ticker, "name": name, "url": morningstar_url(ticker, kind)}
    try:
        close = t.history(period="13mo")["Close"].dropna()
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

import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------
# User's Investment Portfolio
# ------------------------------
portfolio = {
    "Gold": {
        "amount_invested": 24000,
        "quantity": 150,  # grams
    },
    "Crypto": {
        "assets": {
            "ethereum": {"symbol": "ethereum", "amount_invested": 2611.23, "quantity": (1460/2661)+(1151.23/1602)},
            "solana": {"symbol": "solana", "amount_invested": 2491.58, "quantity": (1500/168.4)+(991.58/129)},
            "binancecoin": {"symbol": "binancecoin", "amount_invested": 1001.37, "quantity": 1001.37/588},
            "cardano": {"symbol": "cardano", "amount_invested": 591, "quantity": 591/0.6516},
        }
    },
    "ETFs": {
        "NDQ": {"ticker": "NDQ.AX", "amount_invested": 2880},
        "A200": {"ticker": "A200.AX", "amount_invested": 2160},
        "VGS": {"ticker": "VGS.AX", "amount_invested": 2160},
    }
}

# ------------------------------
# Fetch Live Prices
# ------------------------------
def get_gold_price():
    try:
        response = requests.get("https://api.metals.live/v1/spot")
        data = response.json()
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and 'gold' in item:
                    return item['gold']
    except Exception as e:
        print("Gold price fetch error:", e)
    return None  # fallback can be added here if needed

def get_crypto_price(symbol):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
    response = requests.get(url)
    return response.json().get(symbol, {}).get("usd", 0)

def get_etf_price(ticker):
    data = yf.Ticker(ticker).history(period="1d")
    return round(data["Close"].iloc[-1], 2) if not data.empty else 0

# ------------------------------
# Streamlit Dashboard UI
# ------------------------------
st.set_page_config(page_title="My Investment Dashboard", layout="wide")
st.title("💼 Sujan's Investment Tracker")

col1, col2 = st.columns(2)

# Gold Section
gold_price_per_gram = get_gold_price()
if gold_price_per_gram:
    gold_value = gold_price_per_gram * portfolio["Gold"]["quantity"]
    gold_profit = gold_value - portfolio["Gold"]["amount_invested"]
    col1.metric("Gold (150g)", f"${gold_value:,.2f}", f"${gold_profit:,.2f}")
else:
    col1.warning("Could not fetch gold price.")

# Crypto Section
crypto_total = 0
crypto_invested = 0
for name, asset in portfolio["Crypto"]["assets"].items():
    current_price = get_crypto_price(asset["symbol"])
    current_value = current_price * asset["quantity"]
    crypto_total += current_value
    crypto_invested += asset["amount_invested"]
crypto_profit = crypto_total - crypto_invested
col1.metric("Crypto Portfolio", f"${crypto_total:,.2f}", f"${crypto_profit:,.2f}")

# ETF Section
etf_total = 0
etf_invested = 0
for name, etf in portfolio["ETFs"].items():
    price = get_etf_price(etf["ticker"])
    units = etf["amount_invested"] / price if price else 0
    value = units * price
    etf_total += value
    etf_invested += etf["amount_invested"]
etf_profit = etf_total - etf_invested
col1.metric("ETFs (NDQ/A200/VGS)", f"${etf_total:,.2f}", f"${etf_profit:,.2f}")

# Total Summary
total_invested = portfolio["Gold"]["amount_invested"] + crypto_invested + etf_invested
total_value = (gold_value if gold_price_per_gram else 0) + crypto_total + etf_total
total_profit = total_value - total_invested
col2.metric("Total Portfolio Value", f"${total_value:,.2f}", f"${total_profit:,.2f}")

# Pie Chart
st.subheader("📊 Portfolio Allocation")
labels = ["Gold", "Crypto", "ETFs"]
values = [gold_value if gold_price_per_gram else 0, crypto_total, etf_total]
fig, ax = plt.subplots()
ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
ax.axis('equal')
st.pyplot(fig)

st.caption("📅 Updates weekly · Live prices from CoinGecko, Yahoo Finance, and Metals.live")

import streamlit as st
import requests
import pandas as pd
import time
import concurrent.futures
import json
import os
import datetime as dt
import ccxt
import streamlit.components.v1 as components

# ================= KONFIGURASI & THEME ENGINE =================
st.set_page_config(layout="wide", page_title="Apex Predator Institutional", page_icon="🏴‍☠️")

if 'active_theme' not in st.session_state:
    st.session_state.active_theme = "Apex Institutional (Dark)"

def apply_theme(theme_name):
    # Base Streamlit Cleanup
    css = "<style>\n#MainMenu {visibility: hidden;}\nheader {visibility: hidden;}\nfooter {visibility: hidden;}\n"
    
    # Defaults
    bg_app, bg_sidebar, text_color, font_fam, bg_input, border_color, btn_bg, btn_text = (
        "#0E1117", "#161A25", "#FAFAFA", "'Inter', sans-serif", "#1E2532", "#2d3748", "#00ffcc", "#0b0f19"
    )
    
    if theme_name == "Apex Institutional (Dark)":
        bg_app, bg_sidebar, text_color, font_fam, bg_input, border_color, btn_bg, btn_text = (
            "#0E1117", "#12151D", "#FAFAFA", "'Inter', sans-serif", "#1A202C", "#2d3748", "#00ffcc", "#0b0f19"
        )
    elif theme_name == "Hacker / Cyberpunk":
        bg_app, bg_sidebar, text_color, font_fam, bg_input, border_color, btn_bg, btn_text = (
            "#000000", "#050505", "#00FF00", "'Courier New', monospace", "#001100", "#00FF00", "#000000", "#00FF00"
        )
    elif theme_name == "macOS Modern":
        bg_app, bg_sidebar, text_color, font_fam, bg_input, border_color, btn_bg, btn_text = (
            "#F0F2F6", "#FFFFFF", "#1E1E1E", "-apple-system, BlinkMacSystemFont, sans-serif", "#F9FAFB", "#D1D5DB", "#007AFF", "#FFFFFF"
        )
    elif theme_name == "Windows XP Retro":
        bg_app, bg_sidebar, text_color, font_fam, bg_input, border_color, btn_bg, btn_text = (
            "#ECE9D8", "#D4D0C8", "#000000", "'Tahoma', sans-serif", "#FFFFFF", "#808080", "#ECE9D8", "#000000"
        )
    elif theme_name == "Ubuntu Linux":
        bg_app, bg_sidebar, text_color, font_fam, bg_input, border_color, btn_bg, btn_text = (
            "#300A24", "#2C001E", "#FFFFFF", "'Ubuntu', sans-serif", "#430C36", "#E95420", "#E95420", "#FFFFFF"
        )

    text_shadow = "text-shadow: 0 0 4px #00FF00 !important;" if theme_name == "Hacker / Cyberpunk" else ""
    btn_border = "border: 1px solid #00FF00 !important;" if theme_name == "Hacker / Cyberpunk" else ("border: 2px solid #FFFFFF !important; border-right-color: #808080 !important; border-bottom-color: #808080 !important;" if theme_name == "Windows XP Retro" else "border: none !important;")
    
    css += f"""
    /* Target Global Background */
    .stApp, .css-1d391kg, .css-18e3th9 {{
        background-color: {bg_app} !important;
    }}

    /* Target Sidebar Background */
    [data-testid="stSidebar"], .css-1d391kg {{
        background-color: {bg_sidebar} !important;
    }}

    /* Target SEMUA Teks Global (Markdown, Label, Headers) */
    p, span, h1, h2, h3, h4, h5, h6, label, div[data-testid="stMarkdownContainer"] p {{
        color: {text_color} !important;
        font-family: {font_fam} !important;
        {text_shadow}
    }}

    /* Target Teks di dalam Dataframe/Tabel */
    [data-testid="stDataFrame"] div, [data-testid="stDataFrame"] span {{
        color: {text_color} !important;
    }}

    /* Target Teks di Metric (Angka Besar) */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"], [data-testid="stMetric"] div {{
        color: {text_color} !important;
    }}
    
    [data-testid="stMetric"], div[data-testid="stExpander"] {{
        background-color: {bg_sidebar} !important;
        border: 1px solid {border_color} !important;
    }}

    /* Target Input Box, Selectbox, & Button agar tidak menyatu dengan background */
    .stSelectbox div[data-baseweb="select"] > div, 
    .stTextInput input, 
    .stNumberInput input {{
        background-color: {bg_input} !important;
        color: {text_color} !important;
        border: 1px solid {border_color} !important;
    }}

    .stButton > button {{
        background-color: {btn_bg} !important;
        color: {btn_text} !important;
        {btn_border}
    }}
    
    .stButton > button:hover {{
        opacity: 0.8;
    }}

    /* Memaksa teks panjang turun ke baris baru (Anti-Overlap) */
    p, span, div, label {{
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        white-space: normal !important;
    }}

    /* ===== FIX EXPANDER HEADER (Teks saling timpa) ===== */
    div[data-testid="stExpander"] details > summary {{
        white-space: normal !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        line-height: 1.5 !important;
        padding: 12px 16px !important;
        min-height: 48px !important;
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
    }}
    div[data-testid="stExpander"] details > summary span,
    div[data-testid="stExpander"] details > summary p {{
        white-space: normal !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        overflow: visible !important;
        text-overflow: unset !important;
        display: inline !important;
        font-size: 0.95rem !important;
    }}
    div[data-testid="stExpander"] {{
        border-radius: 12px !important;
        overflow: visible !important;
        margin-bottom: 10px !important;
    }}

    /* Memberi jarak aman pada setiap kolom Streamlit */
    [data-testid="column"] {{
        padding: 0 8px !important;
        margin-bottom: 12px !important;
        overflow: visible !important;
    }}

    /* Memperbaiki ukuran font dan jarak pada Metric Cards agar tidak meluber */
    [data-testid="stMetricValue"] {{
        font-size: 1.6rem !important;
        line-height: 1.3 !important;
        overflow: visible !important;
        text-overflow: unset !important;
        white-space: normal !important;
        word-wrap: break-word !important;
    }}
    [data-testid="stMetricLabel"] {{
        font-size: 0.85rem !important;
        word-wrap: break-word !important;
        white-space: normal !important;
        overflow: visible !important;
        line-height: 1.3 !important;
    }}
    [data-testid="stMetric"] {{
        padding: 10px 12px !important;
        border-radius: 12px !important;
        overflow: visible !important;
    }}

    /* Memperbaiki jarak tombol di dalam kolom */
    .stButton > button {{
        width: 100% !important;
        margin-top: 5px !important;
        white-space: normal !important;
        height: auto !important;
        padding: 10px !important;
    }}
    """
    
    if theme_name == "Apex Institutional (Dark)":
        css += """.stTabs [data-baseweb="tab-list"] { border-bottom: 2px solid #2d3748 !important; } .stTabs [data-baseweb="tab"] { background-color: #1a202c !important; } .stTabs [aria-selected="true"] { background-color: #00ffcc !important; } .stTabs [aria-selected="true"] span, .stTabs [aria-selected="true"] p { color: #0b0f19 !important; }"""
    elif theme_name == "Hacker / Cyberpunk":
        css += """.stTabs [data-baseweb="tab-list"] { border-bottom: 1px solid #00FF00 !important; } .stTabs [data-baseweb="tab"] { background-color: #000000 !important; border: 1px solid #00FF00 !important; } .stTabs [aria-selected="true"] { background-color: #00FF00 !important; } .stTabs [aria-selected="true"] span, .stTabs [aria-selected="true"] p { color: #000000 !important; text-shadow: none !important; }"""
    elif theme_name == "macOS Modern":
        css += """.stTabs [data-baseweb="tab-list"] { border-bottom: 2px solid #D1D5DB !important; } .stTabs [data-baseweb="tab"] { background-color: #FFFFFF !important; border: 1px solid #D1D5DB !important; } .stTabs [aria-selected="true"] { background-color: #007AFF !important; } .stTabs [aria-selected="true"] span, .stTabs [aria-selected="true"] p { color: #FFFFFF !important; }"""
    elif theme_name == "Windows XP Retro":
        css += """.stTabs [data-baseweb="tab-list"] { border-bottom: 2px solid #808080 !important; } .stTabs [data-baseweb="tab"] { background-color: #ECE9D8 !important; border: 2px solid #FFFFFF !important; border-right-color: #808080 !important; border-bottom-color: #808080 !important; } .stTabs [aria-selected="true"] { background-color: #0053E5 !important; } .stTabs [aria-selected="true"] span, .stTabs [aria-selected="true"] p { color: #FFFFFF !important; }"""
    elif theme_name == "Ubuntu Linux":
        css += """.stTabs [data-baseweb="tab-list"] { border-bottom: 2px solid #E95420 !important; } .stTabs [data-baseweb="tab"] { background-color: #5E2750 !important; } .stTabs [aria-selected="true"] { background-color: #E95420 !important; } .stTabs [aria-selected="true"] span, .stTabs [aria-selected="true"] p { color: #FFFFFF !important; }"""

    css += """
    @media (max-width: 768px) {
        /* Perkecil font global untuk HP */
        html, body, p, span, div, label {
            font-size: 13px !important;
        }
        
        /* Perkecil judul dan header */
        h1 { font-size: 1.3rem !important; }
        h2 { font-size: 1.1rem !important; }
        h3 { font-size: 1.0rem !important; }

        /* Metrik (Angka besar) harus dikecilkan agar tidak tertindih */
        [data-testid="stMetricValue"] {
            font-size: 1.2rem !important;
            line-height: 1.3 !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.7rem !important;
            white-space: normal !important;
            line-height: 1.2 !important;
        }
        [data-testid="stMetric"] {
            padding: 8px 6px !important;
        }

        /* Expander Header di HP - KRITIS */
        div[data-testid="stExpander"] details > summary {
            padding: 10px 8px !important;
            font-size: 13px !important;
            line-height: 1.4 !important;
        }
        div[data-testid="stExpander"] details > summary span,
        div[data-testid="stExpander"] details > summary p {
            font-size: 12px !important;
            line-height: 1.3 !important;
        }

        /* Tabel / Dataframe HARUS bisa di-scroll ke samping (horizontal scroll) */
        [data-testid="stDataFrame"] {
            width: 100% !important;
            overflow-x: auto !important;
        }

        /* Buat tombol lebih nyaman ditekan dengan jempol (Touch Target) */
        .stButton > button {
            padding: 12px 10px !important;
            font-size: 14px !important;
            font-weight: bold !important;
        }

        /* Hilangkan padding berlebih di pinggir layar HP */
        .stApp {
            padding: 0.5rem 0.3rem !important;
        }

        /* 1. Paksa semua teks turun ke baris baru jika mentok (Jangan ditimpa) */
        p, span, label, div.stMarkdown, div.stText, h1, h2, h3 {
            white-space: normal !important;
            word-wrap: break-word !important;
            overflow-wrap: break-word !important;
            line-height: 1.4 !important;
        }

        /* 2. Perbaikan khusus untuk Checkbox, Toggle, dan Radio Button */
        div[data-testid="stCheckbox"] label, 
        div[data-testid="stToggle"] label, 
        div[data-testid="stRadio"] label {
            white-space: normal !important;
            display: inline-block !important;
            width: 100% !important;
            margin-bottom: 5px !important;
        }

        /* 3. Beri jarak (Padding) ekstra di dalam form API dan Kartu Sinyal */
        div[data-testid="stForm"] {
            padding: 12px 8px !important;
        }
        
        /* 4. Kolom HP: stack vertikal jika terlalu sempit */
        [data-testid="column"] {
            min-width: 100% !important;
            flex: 1 1 100% !important;
            padding: 0 4px !important;
            margin-bottom: 8px !important;
        }

        /* 5. Tab navigation di HP */
        .stTabs [data-baseweb="tab"] {
            font-size: 11px !important;
            padding: 6px 8px !important;
        }
    }
    """

    css += "\n</style>"

    if theme_name == "Apex Institutional (Dark)":
        premium_css = """
        <style>
        /* Background Utama Gelap Murni LuxAlgo */
        .stApp, .css-1d391kg, .css-18e3th9 {
            background: linear-gradient(180deg, #0A0D14 0%, #050608 100%) !important;
        }
        
        /* Glassmorphism pada Kontainer dan Expander */
        [data-testid="stMetric"], div[data-testid="stExpander"], div[data-testid="stForm"] {
            background: rgba(18, 22, 31, 0.6) !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(0, 255, 204, 0.15) !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5) !important;
        }

        /* Border Radius Global & Halus */
        input, select, .stSelectbox div[data-baseweb="select"] > div {
            border-radius: 8px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }

        /* Efek Tombol Neon */
        .stButton > button {
            border-radius: 8px !important;
            transition: all 0.3s ease-in-out !important;
            border: 1px solid transparent !important;
        }
        
        /* Neon Glow saat Hover */
        .stButton > button:hover {
            box-shadow: 0 0 15px rgba(0, 255, 204, 0.6) !important;
            border: 1px solid #00ffcc !important;
            transform: translateY(-2px);
        }
        </style>
        """
        st.markdown(premium_css, unsafe_allow_html=True)

    st.markdown(css, unsafe_allow_html=True)

# Injeksi tema sesegera mungkin
apply_theme(st.session_state.active_theme)

# ================= CONFIG MODUL =================
def load_config():
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            try: return json.load(f)
            except: pass
    return {"bot_token": "", "chat_id": "", "api_key": "", "api_secret": ""}

def save_config(bot_token, chat_id, api_key, api_secret):
    with open("config.json", "w") as f: json.dump({"bot_token": bot_token, "chat_id": chat_id, "api_key": api_key, "api_secret": api_secret}, f)

def send_telegram_alert(bot_token, chat_id, message):
    if not bot_token or not chat_id: return False, "Token atau Chat ID kosong"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": str(chat_id).strip(), "text": message, "parse_mode": "Markdown"}
    try:
        res = requests.post(url, json=payload, timeout=5)
        return (True, "Berhasil") if res.status_code == 200 else (False, f"Telegram menolak: {res.text}")
    except Exception as e:
        return False, f"Koneksi terputus: {str(e)}"

# ================= CCXT BRACKET ORDER ENGINE =================
def format_ccxt_symbol(symbol):
    if symbol.endswith('USDT'):
        base = symbol.replace('USDT', '')
        return f"{base}/USDT:USDT"
    return symbol

def execute_bracket_order(exchange_id, api_key, api_secret, symbol, side, margin_usdt, sl_price, tp_price, is_live):
    if not is_live:
        return True, f"SIMULASI TESTNET: Order {side.upper()} untuk {symbol} sebesar ${margin_usdt} berhasil dikirim (Uang Virtual)."
    
    if not api_key or not api_secret:
        return False, "API Key / Secret Key tidak boleh kosong pada Mode Live."

    try:
        if exchange_id.lower() == "binance":
            exchange = ccxt.binanceusdm({'apiKey': api_key, 'secret': api_secret, 'enableRateLimit': True, 'options': {'defaultType': 'future'}})
        elif exchange_id.lower() == "bybit":
            exchange = ccxt.bybit({'apiKey': api_key, 'secret': api_secret, 'enableRateLimit': True, 'options': {'defaultType': 'future'}})
        else:
            return False, f"Bursa {exchange_id} saat ini belum mendukung Auto Execution."
        
        ccxt_symbol = format_ccxt_symbol(symbol)
        markets = exchange.load_markets()
        if ccxt_symbol not in markets:
            return False, f"Simbol {ccxt_symbol} tidak ditemukan di bursa {exchange_id}."
            
        ticker = exchange.fetch_ticker(ccxt_symbol)
        current_price = float(ticker['last'])
        
        raw_qty = margin_usdt / current_price
        qty_str = exchange.amount_to_precision(ccxt_symbol, raw_qty)
        qty = float(qty_str)
        
        if qty <= 0: return False, "Margin USDT terlalu kecil, perhitungan lot menjadi 0."

        close_side = 'sell' if side.lower() == 'buy' else 'buy'
        
        # 1. Entry Market
        try: exchange.create_market_order(ccxt_symbol, side, qty)
        except Exception as e: return False, f"Gagal Eksekusi Entry Market: {str(e)}"
            
        # 2. SL Market (Reduce Only)
        try: exchange.create_order(ccxt_symbol, 'STOP_MARKET', close_side, qty, None, {'stopPrice': sl_price, 'reduceOnly': True})
        except Exception as e: return False, f"Entry Berhasil, tapi SL Gagal: {str(e)}"
            
        # 3. TP Market (Reduce Only)
        try: exchange.create_order(ccxt_symbol, 'TAKE_PROFIT_MARKET', close_side, qty, None, {'stopPrice': tp_price, 'reduceOnly': True})
        except Exception as e: return False, f"Entry & SL Berhasil, tapi TP Gagal: {str(e)}"
            
        return True, f"LIVE EXECUTION SUKSES! Entry {side.upper()} {qty} {ccxt_symbol} di harga {current_price}."
        
    except Exception as e:
        return False, f"API ERROR: {str(e)}"

# ================= ADAPTER UNIVERSAL =================
def get_exchange_interval(exchange, tf):
    mapping = {"Binance": {"5m": "5m", "15m": "15m", "1H": "1h"}, "BingX": {"5m": "5m", "15m": "15m", "1H": "1h"}, "Bybit": {"5m": "5", "15m": "15", "1H": "60"}, "OKX": {"5m": "5m", "15m": "15m", "1H": "1H"}, "LBank": {"5m": "minute5", "15m": "minute15", "1H": "hour1"}}
    return mapping.get(exchange, {}).get(tf, "1h")

@st.cache_data(ttl=300, show_spinner=False)
def get_top_coins(exchange, limit):
    try:
        if exchange == "Binance": return [d['symbol'] for d in sorted([d for d in requests.get("https://data-api.binance.vision/api/v3/ticker/24hr", timeout=10).json() if d['symbol'].endswith('USDT')], key=lambda x: float(x['quoteVolume']), reverse=True)[:limit]]
        elif exchange == "BingX": return [d['symbol'] for d in sorted([d for d in requests.get("https://open-api.bingx.com/openApi/swap/v2/quote/ticker", timeout=10).json().get("data", []) if "USDT" in d['symbol']], key=lambda x: float(x['volume']), reverse=True)[:limit]]
        elif exchange == "Bybit": return [d['symbol'] for d in sorted([d for d in requests.get("https://api.bytick.com/v5/market/tickers?category=linear", timeout=10).json().get("result", {}).get("list", []) if d['symbol'].endswith('USDT')], key=lambda x: float(x.get('turnover24h', 0)), reverse=True)[:limit]]
        elif exchange == "OKX": return [d['instId'] for d in sorted([d for d in requests.get("https://www.okx.com/api/v5/market/tickers?instType=SWAP", timeout=10).json().get("data", []) if "USDT" in d['instId']], key=lambda x: float(x.get('volCcy24h', 0)), reverse=True)[:limit]]
        elif exchange == "LBank": return [d['symbol'] for d in sorted([d for d in requests.get("https://api.lbkex.com/v2/ticker/24hr.do", timeout=10).json().get("data", []) if d['symbol'].endswith('_usdt')], key=lambda x: float(x.get('ticker', {}).get('vol', 0)), reverse=True)[:limit]]
    except: return []

def fetch_data_from_exchange(exchange, symbol, tf, limit=100):
    try:
        interval = get_exchange_interval(exchange, tf)
        df = pd.DataFrame()
        if exchange == "Binance":
            res = requests.get("https://data-api.binance.vision/api/v3/klines", params={"symbol": symbol, "interval": interval, "limit": limit}, timeout=10)
            if res.status_code == 200: df = pd.DataFrame(res.json(), columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'c_time', 'q_vol', 'trades', 'tb', 'tq', 'i'])
        elif exchange == "BingX":
            res = requests.get("https://open-api.bingx.com/openApi/swap/v3/quote/klines", params={"symbol": symbol, "interval": interval, "limit": limit}, timeout=10)
            if res.status_code == 200: df = pd.DataFrame(res.json().get("data", [])).rename(columns={"time": "Timestamp", "open": "Open", "high": "High", "low": "Low", "close": "Close", "volume": "Volume"})
        elif exchange == "Bybit":
            res = requests.get("https://api.bytick.com/v5/market/kline", params={"category": "linear", "symbol": symbol, "interval": interval, "limit": limit}, timeout=10)
            if res.status_code == 200: df = pd.DataFrame(reversed(res.json().get("result", {}).get("list", [])), columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'turnover'])
        elif exchange == "OKX":
            res = requests.get("https://www.okx.com/api/v5/market/candles", params={"instId": symbol, "bar": interval, "limit": limit}, timeout=10)
            if res.status_code == 200: df = pd.DataFrame(reversed(res.json().get("data", [])), columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'vc', 'vcq', 'c'])
        elif exchange == "LBank":
            res = requests.get("https://api.lbkex.com/v2/kline.do", params={"symbol": symbol, "type": interval, "size": limit}, timeout=10)
            if res.status_code == 200:
                df = pd.DataFrame(res.json().get("data", []), columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
                if not df.empty: df['Timestamp'] = df['Timestamp'].astype(float) * 1000

        if not df.empty:
            df = df[['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']].copy()
            df['Close'] = df['Close'].astype(float)
            df['Volume'] = df['Volume'].astype(float)
            return df
        return None
    except: return None

# ================= MULTI-STRATEGY ENGINE =================
def calculate_signals(df):
    df = df.copy()
    df['SMA_20'] = df['Close'].rolling(window=20).mean(); df['STD_20'] = df['Close'].rolling(window=20).std()
    df['Upper_BB'] = df['SMA_20'] + (df['STD_20'] * 2); df['Lower_BB'] = df['SMA_20'] - (df['STD_20'] * 2)
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0.0).ewm(alpha=1/14, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0.0)).ewm(alpha=1/14, adjust=False).mean()
    df['RSI_14'] = 100 - (100 / (1 + (gain/loss)))
    df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean(); df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
    df['MACD'] = df['Close'].ewm(span=12, adjust=False).mean() - df['Close'].ewm(span=26, adjust=False).mean()
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['Vol_SMA_20'] = df['Volume'].rolling(window=20).mean()
    df['Max_20'] = df['Close'].rolling(20).max().shift(1); df['Min_20'] = df['Close'].rolling(20).min().shift(1)

    latest, prev = df.iloc[-1], df.iloc[-2]
    signals = {}
    
    if latest['Close'] < latest['Lower_BB'] and latest['RSI_14'] < 30: signals['Mean Reversion'] = "LONG 🟢"
    elif latest['Close'] > latest['Upper_BB'] and latest['RSI_14'] > 70: signals['Mean Reversion'] = "SHORT 🔴"

    if latest['EMA_9'] > latest['EMA_21'] and prev['EMA_9'] <= prev['EMA_21'] and latest['MACD'] > latest['Signal_Line']: signals['Trend Following'] = "LONG 🟢"
    elif latest['EMA_9'] < latest['EMA_21'] and prev['EMA_9'] >= prev['EMA_21'] and latest['MACD'] < latest['Signal_Line']: signals['Trend Following'] = "SHORT 🔴"

    if latest['Volume'] > (2 * latest['Vol_SMA_20']) and latest['Vol_SMA_20'] > 0:
        if latest['Close'] > prev['Close'] and latest['Close'] > latest['Max_20']: signals['Volume Breakout'] = "LONG 🟢"
        elif latest['Close'] < prev['Close'] and latest['Close'] < latest['Min_20']: signals['Volume Breakout'] = "SHORT 🔴"

    return signals, latest['Close']

def process_coin_scan(exchange, symbol, tf, tp_mode, sl_pct, tp_pct, tsl_act_pct, tsl_step_pct, bot_token, chat_id):
    df_scan = fetch_data_from_exchange(exchange, symbol, tf, limit=100)
    if df_scan is None or len(df_scan) < 50: return []
        
    signals_found, entry = calculate_signals(df_scan)
    if not signals_found: return []
    
    results = []
    for strat, signal in signals_found.items():
        res_dict = {
            "Exchange": exchange, "Koin": symbol, "Strategi": strat, "Sinyal": signal,
            "Entry": float(f"{entry:.5f}")
        }
        if tp_mode == "Statis":
            sl = entry * (1 - (sl_pct / 100)) if "LONG" in signal else entry * (1 + (sl_pct / 100))
            tp = entry * (1 + (tp_pct / 100)) if "LONG" in signal else entry * (1 - (tp_pct / 100))
            res_dict.update({"SL": float(f"{sl:.5f}"), "Harga TP": float(f"{tp:.5f}")})
            tp_msg = f"*TP:* {tp:.5f}"
        else:
            sl = entry * (1 - (sl_pct / 100)) if "LONG" in signal else entry * (1 + (sl_pct / 100))
            tsl = entry * (1 + (tsl_act_pct / 100)) if "LONG" in signal else entry * (1 - (tsl_act_pct / 100))
            res_dict.update({"SL": float(f"{sl:.5f}"), "TSL Trigger": float(f"{tsl:.5f}"), "Step Area": float(f"{tsl_step_pct:.2f}")})
            tp_msg = f"*TSL Trigger:* {tsl:.5f}\n*Step Area:* {tsl_step_pct}%"
            
        results.append(res_dict)
        if bot_token and chat_id:
            msg = f"🚨 *NEW SIGNAL FOUND* 🚨\n*Bursa:* {exchange}\n*Koin:* {symbol}\n*Strategi:* {strat}\n*Sinyal:* {signal}\n*Entry:* {entry:.5f}\n*SL:* {sl:.5f}\n{tp_msg}"
            send_telegram_alert(bot_token, chat_id, msg)
    return results

# ================= BACKTESTER =================
@st.cache_data(ttl=3600, show_spinner=False)
def get_historical_data_universal(exchange, symbol, tf, days=90):
    if exchange == "Binance":
        end_time = int(time.time() * 1000); start_time = end_time - (days * 24 * 60 * 60 * 1000)
        all_klines, current_start = [], start_time
        while current_start < end_time:
            try:
                res = requests.get("https://data-api.binance.vision/api/v3/klines", params={"symbol": symbol, "interval": get_exchange_interval("Binance", tf), "startTime": current_start, "endTime": end_time, "limit": 1000}, timeout=10)
                if res.status_code != 200: break
                data = res.json()
                if not data: break
                all_klines.extend(data); current_start = data[-1][0] + 1; time.sleep(0.01)
            except: break
        if not all_klines: return pd.DataFrame()
        df = pd.DataFrame(all_klines, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close_Time', 'QAV', 'NoT', 'TBB', 'TBQ', 'I'])
        df.drop_duplicates(subset=['Timestamp'], inplace=True)
        df = df[['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']]
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
        return df.astype({'Open': float, 'High': float, 'Low': float, 'Close': float, 'Volume': float})
    else:
        df = fetch_data_from_exchange(exchange, symbol, tf, limit=1000)
        if df is not None: df['Timestamp'] = pd.to_datetime(df['Timestamp'].astype(float), unit='ms')
        return df

@st.cache_data(show_spinner=False)
def run_strategy_backtest(df, strategy, tp_mode, sl_pct, tp_pct, tsl_act_pct, tsl_step_pct):
    df = df.copy()
    if len(df) == 0: return 0.0, 0
    df['SMA_20'] = df['Close'].rolling(window=20).mean(); df['STD_20'] = df['Close'].rolling(window=20).std()
    df['Upper_BB'] = df['SMA_20'] + (df['STD_20'] * 2); df['Lower_BB'] = df['SMA_20'] - (df['STD_20'] * 2)
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0.0).ewm(alpha=1/14, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0.0)).ewm(alpha=1/14, adjust=False).mean()
    df['RSI_14'] = 100 - (100 / (1 + (gain/loss)))
    df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean(); df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
    df['MACD'] = df['Close'].ewm(span=12, adjust=False).mean() - df['Close'].ewm(span=26, adjust=False).mean()
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['Vol_SMA_20'] = df['Volume'].rolling(window=20).mean()
    df['Max_20'] = df['Close'].rolling(20).max().shift(1); df['Min_20'] = df['Close'].rolling(20).min().shift(1)
    df.dropna(inplace=True); df.reset_index(drop=True, inplace=True)
    
    capital, pos_type, pos_size, entry_price, sl_price, tp_price, tsl_active = 1000.0, None, 0.0, 0.0, 0.0, 0.0, False
    total_trades, win_trades = 0, 0
    
    for i in range(1, len(df)):
        c = df.loc[i, 'Close']
        if pos_type is None:
            sig = None
            if strategy == 'Mean Reversion':
                if c < df.loc[i, 'Lower_BB'] and df.loc[i, 'RSI_14'] < 30: sig = 'LONG'
                elif c > df.loc[i, 'Upper_BB'] and df.loc[i, 'RSI_14'] > 70: sig = 'SHORT'
            elif strategy == 'Trend Following':
                if df.loc[i, 'EMA_9'] > df.loc[i, 'EMA_21'] and df.loc[i-1, 'EMA_9'] <= df.loc[i-1, 'EMA_21'] and df.loc[i, 'MACD'] > df.loc[i, 'Signal_Line']: sig = 'LONG'
                elif df.loc[i, 'EMA_9'] < df.loc[i, 'EMA_21'] and df.loc[i-1, 'EMA_9'] >= df.loc[i-1, 'EMA_21'] and df.loc[i, 'MACD'] < df.loc[i, 'Signal_Line']: sig = 'SHORT'
            elif strategy == 'Volume Breakout':
                if df.loc[i, 'Volume'] > (2 * df.loc[i, 'Vol_SMA_20']) and df.loc[i, 'Vol_SMA_20'] > 0:
                    if c > df.loc[i-1, 'Close'] and c > df.loc[i, 'Max_20']: sig = 'LONG'
                    elif c < df.loc[i-1, 'Close'] and c < df.loc[i, 'Min_20']: sig = 'SHORT'
            if sig == 'LONG':
                pos_type = 'LONG'; pos_size = capital / c; entry_price = c; capital = 0.0; tsl_active = False
                sl_price = c * (1 - (sl_pct / 100)); tp_price = c * (1 + (tp_pct / 100))
            elif sig == 'SHORT':
                pos_type = 'SHORT'; pos_size = capital / c; entry_price = c; capital = 0.0; tsl_active = False
                sl_price = c * (1 + (sl_pct / 100)); tp_price = c * (1 - (tp_pct / 100))
                
        elif pos_type == 'LONG':
            if tp_mode == "Statis":
                if c <= sl_price: capital = pos_size * c; total_trades += 1; pos_type = None
                elif c >= tp_price: capital = pos_size * c; win_trades += 1; total_trades += 1; pos_type = None
            else:
                if c <= sl_price:
                    capital = pos_size * c; total_trades += 1; win_trades += 1 if c > entry_price else 0; pos_type = None
                elif not tsl_active and c >= entry_price * (1 + (tsl_act_pct / 100)):
                    tsl_active = True; sl_price = c * (1 - (tsl_step_pct / 100))
                elif tsl_active: sl_price = max(sl_price, c * (1 - (tsl_step_pct / 100)))

        elif pos_type == 'SHORT':
            if tp_mode == "Statis":
                if c >= sl_price: capital = pos_size * (2 * entry_price - c); total_trades += 1; pos_type = None
                elif c <= tp_price: capital = pos_size * (2 * entry_price - c); win_trades += 1; total_trades += 1; pos_type = None
            else:
                if c >= sl_price:
                    capital = pos_size * (2 * entry_price - c); total_trades += 1; win_trades += 1 if c < entry_price else 0; pos_type = None
                elif not tsl_active and c <= entry_price * (1 - (tsl_act_pct / 100)):
                    tsl_active = True; sl_price = c * (1 + (tsl_step_pct / 100))
                elif tsl_active: sl_price = min(sl_price, c * (1 + (tsl_step_pct / 100)))

    if pos_type == 'LONG':
        c = df.iloc[-1]['Close']; total_trades += 1; win_trades += 1 if c > entry_price else 0
    elif pos_type == 'SHORT':
        c = df.iloc[-1]['Close']; total_trades += 1; win_trades += 1 if c < entry_price else 0
        
    return (win_trades / total_trades * 100) if total_trades > 0 else 0.0, total_trades

def calculate_kelly_fraction(win_rate_pct, rr_ratio):
    w = win_rate_pct / 100
    if rr_ratio <= 0: return 0.0
    return max(0.0, ((w - ((1 - w) / rr_ratio)) / 2) * 100)

# ================= MACRO & ARBITRAGE =================
def fetch_economic_calendar():
    now = dt.datetime.now()
    data = [
        {"Tanggal & Waktu (WIB)": (now - dt.timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"), "Dampak": "🟡 Med", "Nama Event / Berita": "SOL Token Unlock ($1.2M)"},
        {"Tanggal & Waktu (WIB)": (now + dt.timedelta(minutes=45)).strftime("%Y-%m-%d %H:%M:%S"), "Dampak": "🔴 High", "Nama Event / Berita": "US Core CPI (Inflation)"},
        {"Tanggal & Waktu (WIB)": now.strftime("%Y-%m-%d %H:%M:%S"), "Dampak": "🔴 High", "Nama Event / Berita": "FOMC Rate Decision"},
    ]
    df = pd.DataFrame(data); df['Waktu_Sort'] = pd.to_datetime(df['Tanggal & Waktu (WIB)'])
    return df.sort_values(by='Waktu_Sort').drop(columns=['Waktu_Sort']).reset_index(drop=True)

def check_kill_switch_from_calendar(df_cal):
    now = dt.datetime.now()
    for _, row in df_cal[df_cal['Dampak'] == '🔴 High'].iterrows():
        if abs((now - pd.to_datetime(row['Tanggal & Waktu (WIB)'])).total_seconds()) <= 15 * 60: return True, row['Nama Event / Berita']
    return False, None

def scan_arbitrage():
    coins = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'XRPUSDT', 'DOGEUSDT']
    data = []
    try: bin_prices = {d['symbol']: float(d['price']) for d in requests.get("https://data-api.binance.vision/api/v3/ticker/price", timeout=5).json() if d['symbol'] in coins}
    except: bin_prices = {}
    try: by_prices = {d['symbol']: float(d['lastPrice']) for d in requests.get("https://api.bytick.com/v5/market/tickers?category=linear", timeout=5).json().get("result", {}).get("list", []) if d['symbol'] in coins}
    except: by_prices = {}

    for coin in coins:
        bp, by = bin_prices.get(coin), by_prices.get(coin)
        if bp and by:
            data.append({"Koin": coin, "Buy (Limit)": "Binance" if bp < by else "Bybit", "Sell (Limit)": "Bybit" if bp < by else "Binance", "Spread (%)": float(f"{(abs(bp - by) / min(bp, by) * 100):.4f}"), "Net Profit (%)": float(f"{(abs(bp - by) / min(bp, by) * 100):.4f}")})
    return pd.DataFrame(data).sort_values(by="Net Profit (%)", ascending=False)

# ================= UI HELPER: SIGNAL CARDS =================
def render_signal_card(data, is_live, api_key, api_secret, tp_mode, index):
    wr_str = f" | WR: {data['Win Rate (%)']:.1f}%" if 'Win Rate (%)' in data else ""
    with st.expander(f"⚡ {data['Sinyal']} | {data['Koin']} ({data['Exchange']}){wr_str}", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Entry", f"{data['Entry']:.5f}")
        c2.metric("Stop Loss", f"{data['SL']:.5f}")
        target_val = data.get('Target/TSL', data.get('Harga TP', data.get('TSL Trigger', 0)))
        c3.metric("Target/TSL" if tp_mode == "Trailing Stop" else "Take Profit", f"{target_val:.5f}")
        if 'Win Rate (%)' in data: c4.metric("Win Rate", f"{data['Win Rate (%)']:.1f}%")
        
        st.markdown("---")
        cc1, cc2 = st.columns([1, 2])
        strat_key = data.get('Strategi Terbaik', data.get('Strategi'))
        with cc1: margin = st.number_input("Margin (USDT)", value=50.0, step=10.0, key=f"m_{strat_key}_{data['Koin']}_{index}")
        with cc2:
            st.write(""); st.write("")
            side = "buy" if "LONG" in data['Sinyal'] else "sell"
            if st.button(f"{'🟢' if side=='buy' else '🔴'} EXECUTE {side.upper()} - {data['Koin']}", key=f"btn_{strat_key}_{data['Koin']}_{index}", use_container_width=True, disabled=not st.session_state.api_connected):
                with st.spinner("Mengirim perintah eksekusi..."):
                    success, msg = execute_bracket_order(data['Exchange'], api_key, api_secret, data['Koin'], side, margin, data['SL'], target_val, is_live)
                    if success: st.success(msg)
                    else: st.error(msg)

        # ===== STEALTH CHART MODE =====
        with st.expander(f"📊 Chart & Analisis Teknikal: {data['Koin']}", expanded=False):
            # BAGIAN 1: Detail Strategi
            strat_name = data.get('Strategi Terbaik', data.get('Strategi', 'N/A'))
            signal_dir = "Bullish (LONG)" if "LONG" in data['Sinyal'] else "Bearish (SHORT)"
            wr_display = f"{data['Win Rate (%)']:.1f}%" if 'Win Rate (%)' in data else "N/A"
            kelly_display = f"{data['Saran Taruhan (%)']:.1f}%" if 'Saran Taruhan (%)' in data else "N/A"
            
            st.markdown(f"""
            **🧠 Strategi Diterapkan:** `{strat_name}`  
            **📈 Arah Sinyal:** `{signal_dir}`  
            **🎯 Win Rate Historis:** `{wr_display}`  
            **💰 Kelly Criterion (Saran Taruhan):** `{kelly_display}`  
            
            **Indikator Pendukung:**
            - **RSI 14:** {'< 30 (Oversold Zone)' if strat_name == 'Mean Reversion' and 'LONG' in data['Sinyal'] else '> 70 (Overbought Zone)' if strat_name == 'Mean Reversion' and 'SHORT' in data['Sinyal'] else 'Confluence Confirmed'}
            - **MACD:** {'Bullish Crossover' if 'LONG' in data['Sinyal'] else 'Bearish Crossover'}
            - **Bollinger Bands:** {'Harga di bawah Lower Band' if strat_name == 'Mean Reversion' and 'LONG' in data['Sinyal'] else 'Harga di atas Upper Band' if strat_name == 'Mean Reversion' and 'SHORT' in data['Sinyal'] else 'Squeeze / Breakout Detected'}
            - **Volume:** {'Spike > 2x rata-rata (Breakout Confirmed)' if strat_name == 'Volume Breakout' else 'Normal'}
            """)
            
            st.markdown("---")
            
            # BAGIAN 2: Grafik TradingView Interaktif
            render_tradingview_chart(data['Koin'], index)

# ================= TRADINGVIEW INTEGRATION =================
def render_tradingview_chart(symbol, chart_id="main"):
    # Normalisasi simbol: hapus /, -, spasi, dan paksa format BINANCE:XXXUSDT
    clean_symbol = symbol.replace("/", "").replace("-", "").replace(" ", "").upper()
    tv_symbol = f"BINANCE:{clean_symbol}"
    # Buat ID unik untuk container agar tidak bentrok antar chart
    container_id = f"tv_{clean_symbol}_{chart_id}".replace(" ", "_")
    
    html_code = f"""
    <div class="tradingview-widget-container" style="height: 500px; width: 100%; border-radius: 12px; overflow: hidden; border: 1px solid rgba(255,255,255,0.1);">
      <div id="{container_id}" style="height: 100%; width: 100%;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget(
      {{
      "autosize": true,
      "symbol": "{tv_symbol}",
      "interval": "15",
      "timezone": "Etc/UTC",
      "theme": "dark",
      "style": "1",
      "locale": "en",
      "enable_publishing": false,
      "backgroundColor": "rgba(10, 13, 20, 1)",
      "gridColor": "rgba(255, 255, 255, 0.06)",
      "hide_top_toolbar": false,
      "hide_legend": false,
      "save_image": false,
      "container_id": "{container_id}",
      "studies": [
        "Volume@tv-basicstudies",
        "RSI@tv-basicstudies",
        "BB@tv-basicstudies"
      ]
    }}
      );
      </script>
    </div>
    """
    components.html(html_code, height=500)

# ================= APP START =================
st.markdown("<h1 style='text-align: center;'>🏴‍☠️ THE APEX PREDATOR TERMINAL</h1>", unsafe_allow_html=True)

if 'scan_results' not in st.session_state: st.session_state.scan_results = []
if 'conviction_picks' not in st.session_state: st.session_state.conviction_picks = []
if 'active_trades' not in st.session_state: st.session_state.active_trades = []
if 'sniper_logs' not in st.session_state: st.session_state.sniper_logs = []
if 'api_connected' not in st.session_state: st.session_state.api_connected = False
if 'exchange_client' not in st.session_state: st.session_state.exchange_client = None

df_calendar = fetch_economic_calendar()
is_kill_switch_active, active_event_name = check_kill_switch_from_calendar(df_calendar)

# ================= SIDEBAR =================
st.sidebar.markdown("<h2 style='text-align: center;'>⚙️ Control Panel</h2>", unsafe_allow_html=True)

# THEME SELECTOR
new_theme = st.sidebar.selectbox("🎨 Tema Terminal", 
    ["Apex Institutional (Dark)", "Hacker / Cyberpunk", "macOS Modern", "Windows XP Retro", "Ubuntu Linux"],
    index=["Apex Institutional (Dark)", "Hacker / Cyberpunk", "macOS Modern", "Windows XP Retro", "Ubuntu Linux"].index(st.session_state.active_theme)
)
if new_theme != st.session_state.active_theme:
    st.session_state.active_theme = new_theme
    st.rerun()

st.sidebar.write("---")

app_config = load_config()

st.sidebar.markdown("### ⚡ API Execution Engine")
with st.sidebar.expander("🔑 Setup Exchange API", expanded=True):
    with st.form(key='api_form'):
        api_key_input = st.text_input("API Key (Binance/Bybit Futures)", value=app_config.get("api_key", ""), type="password")
        api_secret_input = st.text_input("Secret Key", value=app_config.get("api_secret", ""), type="password")
        is_testnet = st.checkbox("🟢 Mode Testnet (Uang Virtual)", value=True)
        submit_api = st.form_submit_button("🔌 HUBUNGKAN & VERIFIKASI")

    if submit_api:
        if not api_key_input or not api_secret_input:
            st.session_state.api_connected = False
            st.error("❌ API Key dan Secret Key tidak boleh kosong.")
        else:
            try:
                exchange = ccxt.binanceusdm({
                    'apiKey': api_key_input,
                    'secret': api_secret_input,
                    'enableRateLimit': True,
                    'options': {'defaultType': 'future'}
                })
                exchange.set_sandbox_mode(is_testnet)
                exchange.load_markets() # Test connection
                st.session_state.api_connected = True
                st.session_state.exchange_client = exchange
                st.success("✅ Terhubung ke Server Eksekusi!")
            except Exception as e:
                st.session_state.api_connected = False
                st.error("❌ Gagal Terhubung: Periksa API Key atau koneksi internet.")
                
live_mode = not is_testnet if 'is_testnet' in locals() else False

st.sidebar.markdown("### 🤖 Auto-Sniper Bot")
auto_sniper_active = st.sidebar.toggle("🤖 AUTO-SNIPER MODE (OTOMATIS TRADE)", value=False, disabled=not st.session_state.api_connected)
if auto_sniper_active:
    st.sidebar.error("⚠️ PERINGATAN: AUTO-SNIPER AKTIF! Sistem akan otomatis membuka posisi jika Win Rate > 75%.")
max_open_pos = st.sidebar.number_input("Max Open Positions", value=3, step=1)
margin_per_trade = st.sidebar.number_input("Margin per Auto-Trade (USDT)", value=50.0, step=10.0)

if len(st.session_state.sniper_logs) > 0:
    st.sidebar.markdown("### 📜 Sniper Execution Log")
    for log in reversed(st.session_state.sniper_logs[-10:]):  # Display the last 10 logs
        st.sidebar.info(log)

st.sidebar.markdown("### 💬 Telegram Alerts")
with st.sidebar.expander("⚙️ Telegram Setup", expanded=False):
    bot_token_input = st.text_input("Bot Token", value=app_config.get("bot_token", ""), type="password")
    chat_id_input = st.text_input("Chat ID", value=app_config.get("chat_id", ""))

if st.sidebar.button("💾 Simpan Konfigurasi (API & Telegram)", use_container_width=True):
    save_config(bot_token_input, chat_id_input, api_key_input, api_secret_input)
    st.sidebar.success("Konfigurasi Tersimpan!")

st.sidebar.markdown("### 🌐 Global Feed")
exchanges = st.sidebar.multiselect("Bursa Sasaran", ["Binance", "Bybit"], default=["Binance"])
timeframe = st.sidebar.selectbox("Timeframe", ["5m", "15m", "1H"])
skala_scanner = st.sidebar.selectbox("Kapasitas Koin", [20, 50])

st.sidebar.markdown("### 🎯 Profit Engine Mode")
tp_mode = st.sidebar.radio("Mode Eksekusi Target:", ["Statis", "Trailing Stop"])
sl_pct = st.sidebar.number_input("🔴 Stop Loss (%)", value=2.0, step=0.1)

if tp_mode == "Statis":
    tp_pct = st.sidebar.number_input("🟢 Target TP (%)", value=6.0, step=0.1)
    tsl_act_pct, tsl_step_pct = 0.0, 0.0
else:
    tp_pct = 0.0
    tsl_act_pct = st.sidebar.number_input("🟢 Trailing Activation (%)", value=4.0, step=0.1)
    tsl_step_pct = st.sidebar.number_input("🔄 Trailing Step (%)", value=1.0, step=0.1)

st.sidebar.write("---")
if st.sidebar.button("🚀 EXECUTE MULTI-STRATEGY SCAN", use_container_width=True, type="primary"):
    if is_kill_switch_active: st.sidebar.warning(f"📊 Radar: Ada rilis berita {active_event_name} hari ini. Volatilitas tinggi diperkirakan.")
    if not exchanges: st.sidebar.warning("Pilih bursa!")
    else:
        target_tasks = [(ex, coin) for ex in exchanges for coin in get_top_coins(ex, limit=skala_scanner)]
        temp_results = []
        progress_bar = st.sidebar.progress(0)
        with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
            futures = {executor.submit(process_coin_scan, t[0], t[1], timeframe, tp_mode, sl_pct, tp_pct, tsl_act_pct, tsl_step_pct, app_config.get("bot_token", ""), app_config.get("chat_id", "")): t for t in target_tasks}
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                if len(target_tasks) > 0: progress_bar.progress((i + 1) / len(target_tasks))
                try: 
                    res = future.result()
                    if res: temp_results.extend(res)
                except: pass
        st.session_state.scan_results = temp_results
        st.session_state.conviction_picks = [] 
        st.sidebar.success(f"Scan selesai! {len(temp_results)} sinyal.")

# ================= TAB NAVIGATION =================
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["🏆 Conviction Picks", "🎯 Mean Reversion", "🚀 Trend Follow", "💥 Breakout", "📊 Backtester", "📺 Live Macro", "📆 Calendar", "⚖️ Arbitrage"])

df_all = pd.DataFrame(st.session_state.scan_results)

def render_strategy_tab(strategy_name):
    st.subheader(f"⚡ Sinyal {strategy_name}")
    if is_kill_switch_active: st.warning(f"📊 Radar: Ada rilis berita {active_event_name} hari ini. Volatilitas tinggi diperkirakan.")
    if not df_all.empty and 'Strategi' in df_all.columns:
        sig_data = [row for row in st.session_state.scan_results if row['Strategi'] == strategy_name]
        if not sig_data: st.info("Belum ada sinyal.")
        for idx, data in enumerate(sig_data): render_signal_card(data, live_mode, api_key_input, api_secret_input, tp_mode, f"sig_{strategy_name}_{idx}")

with tab2: render_strategy_tab('Mean Reversion')
with tab3: render_strategy_tab('Trend Following')
with tab4: render_strategy_tab('Volume Breakout')

with tab1:
    st.markdown("## 🏆 Top Conviction Picks")
    if is_kill_switch_active: st.warning(f"📊 Radar: Ada rilis berita {active_event_name} hari ini. Volatilitas tinggi diperkirakan.")
    if st.button("🧠 GENERATE PICKS & AUTO-SNIPER", type="primary"):
        if df_all.empty: st.warning("Jalankan Scanner terlebih dahulu.")
        else:
            conviction_list, grouped, prog = [], df_all.groupby(['Exchange', 'Koin']), st.progress(0)
            for i, ((ex, koin), group) in enumerate(grouped):
                prog.progress((i + 1) / len(grouped))
                df_hist = get_historical_data_universal(ex, koin, timeframe, days=90)
                if df_hist is None or df_hist.empty: continue
                best_strat, best_wr, best_sig = None, -1.0, None
                for _, row in group.iterrows():
                    wr, total_t = run_strategy_backtest(df_hist, row['Strategi'], tp_mode, sl_pct, tp_pct, tsl_act_pct, tsl_step_pct)
                    if wr > best_wr and total_t >= 3: best_wr, best_strat, best_sig = wr, row['Strategi'], row
                if best_strat and best_wr > 0:
                    rr_ratio = (tp_pct / sl_pct) if tp_mode == "Statis" else (tsl_act_pct / sl_pct)
                    target_val = best_sig.get('Harga TP', best_sig.get('TSL Trigger', 0))
                    conviction_list.append({"Exchange": ex, "Koin": koin, "Strategi Terbaik": best_strat, "Win Rate (%)": float(best_wr), "Saran Taruhan (%)": float(calculate_kelly_fraction(best_wr, rr_ratio)), "Sinyal": best_sig['Sinyal'], "Entry": best_sig['Entry'], "SL": best_sig['SL'], "Target/TSL": float(target_val)})
            
            prog.empty()
            st.session_state.conviction_picks = conviction_list
            st.success("Conviction Picks Terbuat!")
            
            # Auto-Sniper Logic
            if auto_sniper_active:
                for data in sorted(conviction_list, key=lambda x: x['Win Rate (%)'], reverse=True):
                    if data['Win Rate (%)'] > 75.0:
                        if data['Koin'] not in st.session_state.active_trades:
                            if len(st.session_state.active_trades) < max_open_pos:
                                side = "buy" if "LONG" in data['Sinyal'] else "sell"
                                success, msg = execute_bracket_order(data['Exchange'], api_key_input, api_secret_input, data['Koin'], side, margin_per_trade, data['SL'], data['Target/TSL'], live_mode)
                                
                                log_time = dt.datetime.now().strftime("%H:%M:%S")
                                if success:
                                    st.session_state.active_trades.append(data['Koin'])
                                    log_str = f"[{log_time}] SNIPED {side.upper()}: {data['Koin']} | Margin: ${margin_per_trade} | Reason: WR {data['Win Rate (%)']:.1f}%"
                                else:
                                    log_str = f"[{log_time}] FAILED {side.upper()}: {data['Koin']} | Error: {msg}"
                                
                                st.session_state.sniper_logs.append(log_str)
                st.rerun() # Refresh untuk memunculkan log di sidebar
            
    if len(st.session_state.conviction_picks) > 0:
        for idx, data in enumerate(sorted(st.session_state.conviction_picks, key=lambda x: x['Win Rate (%)'], reverse=True)):
            render_signal_card(data, live_mode, api_key_input, api_secret_input, tp_mode, f"conv_{idx}")

with tab5:
    st.subheader("📊 Manual Backtester Engine")
    if not df_all.empty and 'Exchange' in df_all.columns:
        pilihan = st.selectbox("Pilih Koin:", (df_all['Exchange'] + " - " + df_all['Koin']).unique())
        strat_pilih = st.selectbox("Pilih Strategi:", ["Mean Reversion", "Trend Following", "Volume Breakout"])
        if st.button("🧪 JALANKAN MANUAL BACKTEST"):
            ex_terpilih, koin_terpilih = pilihan.split(" - ", 1)
            with st.spinner("Menarik data 1 Tahun..."):
                df_hist = get_historical_data_universal(ex_terpilih, koin_terpilih, timeframe, days=365)
            if df_hist is not None and not df_hist.empty:
                wr, total_t = run_strategy_backtest(df_hist, strat_pilih, tp_mode, sl_pct, tp_pct, tsl_act_pct, tsl_step_pct)
                col1, col2 = st.columns(2); col1.metric("Total Trades", total_t); col2.metric("Win Rate", f"{wr:.2f}%")

with tab6: st.subheader("📺 Live Macro Sniper Feed"); st.video("https://www.youtube.com/watch?v=dp8PhLsUcFE")

with tab7:
    st.subheader("📆 Economic & Crypto Event Calendar")
    st.dataframe(df_calendar, use_container_width=True, hide_index=True)

with tab8:
    st.subheader("⚖️ Arbitrage Engine (Maker Fee 0%)")
    if st.button("🔍 SCAN PELUANG ARBITRASE", type="primary"):
        df_arb = scan_arbitrage()
        if not df_arb.empty: st.dataframe(df_arb, use_container_width=True, hide_index=True)
        else: st.warning("Tidak ada spread signifikan.")

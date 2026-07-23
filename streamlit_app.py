import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import pytz
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==============================================================================
# PAGE CONFIGURATION & THEME STATE
# ==============================================================================
st.set_page_config(
    page_title="SK Hynix Arbitrage Hub",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

IS_DARK = st.session_state.theme == "dark"

# ==============================================================================
# CSS DESIGN SYSTEM
# ==============================================================================
def inject_custom_css(is_dark):
    bg = "#09090b" if is_dark else "#ffffff"
    bg_subtle = "#0c0c0f" if is_dark else "#f9fafb"
    card = "#0c0c0f" if is_dark else "#ffffff"
    border = "#1e1e24" if is_dark else "#e4e4e7"
    border_subtle = "#16161a" if is_dark else "#f0f0f2"
    text = "#fafafa" if is_dark else "#09090b"
    text_muted = "#a1a1aa" if is_dark else "#71717a"
    text_dim = "#52525b" if is_dark else "#a1a1aa"
    green = "#22c55e" if is_dark else "#16a34a"
    green_muted = "rgba(34,197,94,0.12)" if is_dark else "rgba(22,163,74,0.08)"
    red = "#ef4444" if is_dark else "#dc2626"
    red_muted = "rgba(239,68,68,0.12)" if is_dark else "rgba(220,38,38,0.08)"
    amber = "#f59e0b" if is_dark else "#d97706"
    amber_muted = "rgba(245,158,11,0.12)" if is_dark else "rgba(217,119,6,0.08)"
    shadow = "none" if is_dark else "0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.03)"
    
    css = f"""
    <style>
    :root {{
        --bg: {bg};
        --bg-subtle: {bg_subtle};
        --card: {card};
        --border: {border};
        --border-subtle: {border_subtle};
        --text: {text};
        --text-muted: {text_muted};
        --text-dim: {text_dim};
        --accent: #2563eb;
        --green: {green};
        --green-muted: {green_muted};
        --red: {red};
        --red-muted: {red_muted};
        --amber: {amber};
        --amber-muted: {amber_muted};
        --shadow: {shadow};
        --radius: 10px;
    }}
    
    /* Hide Streamlit header & decoration */
    header[data-testid="stHeader"], [data-testid="stToolbar"],
    [data-testid="stDecoration"], [data-testid="stStatusWidget"], .stDeployButton {{
        display: none !important;
    }}
    
    /* Global App Styling */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main, .block-container, section[data-testid="stMain"] {{
        background-color: var(--bg) !important;
        color: var(--text) !important;
        font-family: 'DM Sans', -apple-system, sans-serif !important;
    }}
    .block-container {{
        padding: 1.5rem 2rem 2rem !important;
        max-width: 1360px !important;
    }}
    
    /* Pill tabs */
    button[data-baseweb="tab"] {{
        background: transparent !important;
        color: var(--text-muted) !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        padding: 0.6rem 1.2rem !important;
        border: 1px solid transparent !important;
        border-radius: 7px !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: var(--text) !important;
        background: var(--card) !important;
        border-color: var(--border) !important;
    }}
    [data-baseweb="tab-highlight"], [data-baseweb="tab-border"] {{
        display: none !important;
    }}
    [data-baseweb="tab-list"] {{
        gap: 6px !important;
        background: var(--bg-subtle) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        padding: 4px;
    }}
    
    /* Metric Card */
    .metric-card {{
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.1rem 1.25rem;
        box-shadow: var(--shadow);
        margin-bottom: 0.8rem;
    }}
    .metric-label {{
        font-size: 0.78rem;
        color: var(--text-muted);
        font-weight: 600;
        margin-bottom: 0.2rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    .metric-value {{
        font-size: 1.7rem;
        font-weight: 700;
        color: var(--text);
        letter-spacing: -0.03em;
        font-family: 'JetBrains Mono', monospace !important;
    }}
    .metric-delta {{
        font-size: 0.75rem;
        font-weight: 600;
        margin-top: 0.35rem;
        padding: 2px 8px;
        border-radius: 6px;
        display: inline-flex;
        align-items: center;
        gap: 3px;
    }}
    .delta-up {{ color: var(--green); background: var(--green-muted); }}
    .delta-down {{ color: var(--red); background: var(--red-muted); }}
    .delta-warn {{ color: var(--amber); background: var(--amber-muted); }}
    
    /* Chart container */
    .chart-wrap {{
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.2rem 1.2rem 0.6rem;
        box-shadow: var(--shadow);
        margin-bottom: 1.25rem;
    }}
    .chart-title {{
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--text);
    }}
    .chart-subtitle {{
        font-size: 0.72rem;
        color: var(--text-muted);
        margin-bottom: 0.8rem;
    }}
    
    /* Data table styling */
    .data-table {{
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        font-size: 0.82rem;
        margin-top: 0.5rem;
    }}
    .data-table th {{
        text-align: left;
        padding: 0.6rem 0.8rem;
        color: var(--text-muted);
        font-weight: 600;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        border-bottom: 1px solid var(--border);
    }}
    .data-table td {{
        padding: 0.65rem 0.8rem;
        color: var(--text);
        border-bottom: 1px solid var(--border-subtle);
        vertical-align: middle;
    }}
    .data-table tr:last-child td {{
        border-bottom: none;
    }}
    
    /* Badges */
    .badge {{
        display: inline-block;
        padding: 2px 9px;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
    }}
    .badge-green {{ color: var(--green); background: var(--green-muted); }}
    .badge-red {{ color: var(--red); background: var(--red-muted); }}
    .badge-amber {{ color: var(--amber); background: var(--amber-muted); }}
    .badge-blue {{ color: var(--accent); background: rgba(37,99,235,0.1); }}
    
    /* Brand */
    .brand {{
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    .brand-name {{
        font-size: 1.35rem;
        font-weight: 800;
        color: var(--text);
        letter-spacing: -0.04em;
    }}
    .brand-badge {{
        font-size: 0.7rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 20px;
        background: var(--accent);
        color: white;
    }}
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {{
        background-color: var(--bg-subtle) !important;
        border-right: 1px solid var(--border) !important;
    }}
    section[data-testid="stSidebar"] .stButton button {{
        background-color: var(--card) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
    }}
    
    /* Input elements customization */
    .stNumberInput input, .stSelectbox div[data-baseweb="select"] {{
        background-color: var(--bg-subtle) !important;
        color: var(--text) !important;
        border-color: var(--border) !important;
    }}
    
    [data-testid="stHorizontalBlock"] {{
        gap: 1.25rem !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

inject_custom_css(IS_DARK)

# ==============================================================================
# DATA ENGINE (DATA RETRIEVAL & UTILITIES)
# ==============================================================================

@st.cache_data(ttl=15)
def get_live_quote(ticker_symbol):
    """
    Robust live price retrieval from Yahoo Finance.
    Tries multiple fallbacks to ensure data is fetched even if some APIs are throttled.
    """
    ticker = yf.Ticker(ticker_symbol)
    price = None
    prev_close = None
    currency = "USD"
    
    # Method 1: Try fast_info
    try:
        info = ticker.fast_info
        price = info.get('lastPrice') or info.get('last_price')
        prev_close = info.get('previousClose') or info.get('previous_close')
        currency = info.get('currency', currency)
    except Exception:
        pass
        
    # Method 2: Try history
    if price is None or prev_close is None:
        try:
            hist = ticker.history(period="2d")
            if not hist.empty:
                price = hist['Close'].iloc[-1]
                if len(hist) > 1:
                    prev_close = hist['Close'].iloc[-2]
                else:
                    prev_close = hist['Open'].iloc[-1]
        except Exception:
            pass
            
    # Method 3: Try standard info dict
    if price is None:
        try:
            info = ticker.info
            price = info.get('regularMarketPrice') or info.get('currentPrice')
            prev_close = info.get('regularMarketPreviousClose') or info.get('previousClose')
            currency = info.get('currency', currency)
        except Exception:
            pass
            
    # Quick fix for currency defaults if missing
    if ticker_symbol.endswith(".KS"):
        currency = "KRW"
    elif ticker_symbol == "USDKRW=X":
        currency = "KRW"
        
    return {
        "ticker": ticker_symbol,
        "price": price,
        "prev_close": prev_close,
        "currency": currency,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@st.cache_data(ttl=1800) # cache historical data longer (30 mins)
def get_historical_data(ticker_symbol, period="1mo"):
    """
    Fetch historical daily prices.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period=period)
        if not df.empty:
            return df[['Close']]
    except Exception as e:
        st.warning(f"Error fetching history for {ticker_symbol}: {e}")
    return pd.DataFrame()

def get_market_status():
    """
    Timezone-aware market hours calculation.
    Korea (KST): Mon-Fri, 09:00 - 15:30.
    US (EST/EDT): Mon-Fri, 04:00-09:30 (Pre), 09:30-16:00 (Reg), 16:00-20:00 (Post).
    """
    kst = pytz.timezone('Asia/Seoul')
    est = pytz.timezone('America/New_York')
    
    now_utc = datetime.datetime.now(pytz.utc)
    now_kst = now_utc.astimezone(kst)
    now_est = now_utc.astimezone(est)
    
    # Korea Market Hours
    k_weekday = now_kst.weekday()
    k_time = now_kst.time()
    k_open = datetime.time(9, 0)
    k_close = datetime.time(15, 30)
    
    if k_weekday >= 5:
        k_status = "Weekend"
        k_status_class = "badge-red"
    elif k_open <= k_time <= k_close:
        k_status = "Regular Hours"
        k_status_class = "badge-green"
    else:
        k_status = "Closed"
        k_status_class = "badge-red"
        
    # US Market Hours
    u_weekday = now_est.weekday()
    u_time = now_est.time()
    u_pre = datetime.time(4, 0)
    u_reg_open = datetime.time(9, 30)
    u_reg_close = datetime.time(16, 0)
    u_post_close = datetime.time(20, 0)
    
    if u_weekday >= 5:
        u_status = "Weekend"
        u_status_class = "badge-red"
    elif u_reg_open <= u_time <= u_reg_close:
        u_status = "Regular Hours"
        u_status_class = "badge-green"
    elif u_pre <= u_time < u_reg_open:
        u_status = "Pre-Market"
        u_status_class = "badge-amber"
    elif u_reg_close < u_time <= u_post_close:
        u_status = "After-Hours"
        u_status_class = "badge-amber"
    else:
        u_status = "Closed"
        u_status_class = "badge-red"
        
    return {
        "kst_time": now_kst.strftime("%Y-%m-%d %H:%M:%S KST"),
        "est_time": now_est.strftime("%Y-%m-%d %H:%M:%S EST/EDT"),
        "k_status": k_status,
        "k_status_class": k_status_class,
        "u_status": u_status,
        "u_status_class": u_status_class,
        "kst_raw": now_kst,
        "est_raw": now_est
    }

def calculate_change(current, previous):
    if current is None or previous is None or previous == 0:
        return 0.0, "0.00%"
    change = current - previous
    pct = (change / previous) * 100
    sign = "+" if change >= 0 else ""
    return pct, f"{sign}{pct:.2f}%"

def metric_card(label, value, delta=None, delta_type="up"):
    cls = f"delta-{delta_type}"
    arrow = "↑" if delta_type == "up" else ("↓" if delta_type == "down" else "→")
    delta_html = f'<div class="metric-delta {cls}">{arrow} {delta}</div>' if delta else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# SIDEBAR CONTROLS
# ==============================================================================
st.sidebar.markdown("""
<div class="brand">
    <span class="brand-name">Hynix Arbitrage</span>
    <span class="brand-badge">PRO</span>
</div>
""", unsafe_allow_html=True)
st.sidebar.write("")

st.sidebar.subheader("⚙️ Config / 설정")
adr_ticker_choice = st.sidebar.selectbox(
    "ADR Ticker (ADR 티커)",
    ["SKHY", "HXSCF"],
    index=0,
    help="SKHY는 NASDAQ 공식 ADR 티커이며, HXSCF는 OTC(장외시장) 거래 티커입니다."
)

adr_ratio = st.sidebar.number_input(
    "ADR Ratio (본주 대비 비율)",
    min_value=0.01,
    max_value=100.0,
    value=10.0,
    step=1.0,
    help="본주 1주가 나타내는 ADR 수량입니다. SKHY는 1:10 (본주 1주 = 10 ADR) 비율을 가집니다."
)

historical_period = st.sidebar.selectbox(
    "Historical Period (조회 기간)",
    ["5d", "1mo", "3mo", "6mo", "1y"],
    index=1
)

st.sidebar.write("---")

# Refresh button
if st.sidebar.button("🔄 Force Refresh (새로고침)", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# Theme Toggle
theme_label = "☀️ Light Theme" if IS_DARK else "🌙 Dark Theme"
st.sidebar.button(theme_label, on_click=toggle_theme, use_container_width=True)

st.sidebar.markdown(f"""
<div style="font-size:0.72rem; color: #71717a; margin-top:20px;">
    Data source: Yahoo Finance<br>
    Auto-refresh interval: 15s (cached)<br>
    Current user timezone: KST (Seoul)
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# DATA LOADING
# ==============================================================================
with st.spinner("Fetching market data..."):
    # Live prices
    krx_data = get_live_quote("000660.KS")
    adr_data = get_live_quote(adr_ticker_choice)
    fx_data = get_live_quote("USDKRW=X")
    
    # Check if we got valid price data
    data_valid = (
        krx_data['price'] is not None and 
        adr_data['price'] is not None and 
        fx_data['price'] is not None
    )

# ==============================================================================
# MAIN PAGE LAYOUT
# ==============================================================================

# Title Section
t_col1, t_col2 = st.columns([7, 3])
with t_col1:
    st.markdown("""
    <h1 style="font-size:2.0rem; font-weight:800; letter-spacing:-0.05em; margin: 0 0 5px 0;">
        SK Hynix Arbitrage Dashboard
    </h1>
    <p style="font-size:0.85rem; color:#71717a; margin: 0;">
        Real-time calculation of premium/discount based on the Law of One Price (일물일가)
    </p>
    """, unsafe_allow_html=True)

# Timezone & Market Hours Component
m_status = get_market_status()
with t_col2:
    st.markdown(f"""
    <div style="background: var(--card); border: 1px solid var(--border); padding: 0.6rem 0.9rem; border-radius: var(--radius); font-size: 0.76rem; line-height: 1.45;">
        <div>🇰🇷 <b>Seoul (KST):</b> <span style="font-family: monospace;">{m_status['kst_time']}</span> <span class="badge {m_status['k_status_class']}">{m_status['k_status']}</span></div>
        <div style="margin-top:4px;">🇺🇸 <b>New York (EST/EDT):</b> <span style="font-family: monospace;">{m_status['est_time']}</span> <span class="badge {m_status['u_status_class']}">{m_status['u_status']}</span></div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

if not data_valid:
    st.error("⚠️ Failed to retrieve real-time data from Yahoo Finance. Please refresh or try again later.")
    # Show debug info
    st.json({"krx": krx_data, "adr": adr_data, "fx": fx_data})
else:
    # Calculations
    p_krx = krx_data['price']
    p_adr = adr_data['price']
    fx_rate = fx_data['price']
    
    # Calculate returns
    krx_pct, krx_pct_str = calculate_change(p_krx, krx_data['prev_close'])
    adr_pct, adr_pct_str = calculate_change(p_adr, adr_data['prev_close'])
    fx_pct, fx_pct_str = calculate_change(fx_rate, fx_data['prev_close'])
    
    # Implied ADR price in KRW
    # 1 common share = adr_ratio * ADR.
    # So implied share price = adr_ratio * p_adr * fx_rate
    implied_adr_krw = adr_ratio * p_adr * fx_rate
    
    # Premium / Discount Calculation
    # Premium % = ((Implied ADR / KRX Price) - 1) * 100
    premium_pct = ((implied_adr_krw / p_krx) - 1) * 100
    
    # Premium direction & text
    if premium_pct > 0.5:
        prem_status = "Overvalued (할증)"
        prem_class = "delta-down" # selling ADR is recommended, ADR is overvalued
        prem_badge_class = "badge-red"
    elif premium_pct < -0.5:
        prem_status = "Undervalued (할인)"
        prem_class = "delta-up" # buying ADR is recommended, ADR is undervalued
        prem_badge_class = "badge-green"
    else:
        prem_status = "Parity (적정)"
        prem_class = "delta-warn"
        prem_badge_class = "badge-blue"

    # ==========================================================================
    # KPI CARDS ROW
    # ==========================================================================
    kpi_cols = st.columns(4)
    
    # 1. KRX Stock Price
    with kpi_cols[0]:
        delta_type = "up" if krx_pct >= 0 else "down"
        metric_card(
            label="SK Hynix Ordinary (000660.KS)",
            value=f"{p_krx:,.0f} KRW",
            delta=krx_pct_str,
            delta_type=delta_type
        )
        
    # 2. ADR Price
    with kpi_cols[1]:
        delta_type = "up" if adr_pct >= 0 else "down"
        metric_card(
            label=f"SK Hynix ADR ({adr_ticker_choice})",
            value=f"${p_adr:.2f} USD",
            delta=adr_pct_str,
            delta_type=delta_type
        )
        
    # 3. USD/KRW Exchange Rate
    with kpi_cols[2]:
        delta_type = "up" if fx_pct >= 0 else "down"
        metric_card(
            label="USD/KRW Exchange Rate",
            value=f"{fx_rate:,.2f} ₩",
            delta=fx_pct_str,
            delta_type=delta_type
        )
        
    # 4. Arbitrage Premium / Discount
    with kpi_cols[3]:
        delta_type = "down" if premium_pct > 0.5 else ("up" if premium_pct < -0.5 else "warn")
        metric_card(
            label="ADR Premium / Discount",
            value=f"{premium_pct:+.2f}%",
            delta=prem_status,
            delta_type=delta_type
        )

    # ==========================================================================
    # PRICE DIRECTION & RECENTLY TRADED MARKET MOMENTUM
    # ==========================================================================
    # Determine recently active market
    # Korea regular hours: 09:00 - 15:30 KST
    # US regular hours: 22:30 - 05:00 KST (in summer DST)
    kst_now = m_status['kst_raw']
    k_hour = kst_now.hour
    k_minute = kst_now.minute
    k_float_time = k_hour + k_minute / 60.0
    
    # Quick determination of which market is actively trading or recently closed
    recently_active = "Korea (KRX)"
    recently_active_status = "🟢 Regular Trading"
    active_change_str = krx_pct_str
    active_change_val = krx_pct
    
    if m_status['u_status'] == "Regular Hours":
        recently_active = "United States (NASDAQ)"
        recently_active_status = "🟢 Regular Trading"
        active_change_str = adr_pct_str
        active_change_val = adr_pct
    elif m_status['u_status'] in ["Pre-Market", "After-Hours"]:
        recently_active = "United States (NASDAQ)"
        recently_active_status = f"🟡 {m_status['u_status']}"
        active_change_str = adr_pct_str
        active_change_val = adr_pct
    elif m_status['k_status'] == "Closed" and m_status['u_status'] == "Closed":
        # Both closed. Check which one closed last.
        # US closes at 16:00 EST which is 05:00 KST.
        # KRX closes at 15:30 KST.
        # So US closes later than Korea. US is the last active market overnight.
        if 5 <= kst_now.hour < 9:
            recently_active = "United States (NASDAQ)"
            recently_active_status = "🔴 Closed (Last Active)"
            active_change_str = adr_pct_str
            active_change_val = adr_pct
        else:
            recently_active = "Korea (KRX)"
            recently_active_status = "🔴 Closed (Last Active)"
            active_change_str = krx_pct_str
            active_change_val = krx_pct

    direction_arrow = "📈 상승세" if active_change_val > 0 else ("📉 하락세" if active_change_val < 0 else "➡️ 보합")
    direction_color = "var(--green)" if active_change_val > 0 else ("var(--red)" if active_change_val < 0 else "var(--text-muted)")
    
    st.markdown(f"""
    <div style="background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 0.9rem 1.25rem; margin-bottom: 1.25rem; box-shadow: var(--shadow);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
            <div>
                <span style="color: var(--text-muted); font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">최근 거래 시장 방향 (Market Momentum)</span>
                <div style="font-size:1.15rem; font-weight: 700; margin-top:3px; color: var(--text);">
                    현재 주도 시장: <span style="color: var(--accent);">{recently_active}</span> 
                    <span style="font-size: 0.8rem; font-weight: normal; margin-left: 5px;">({recently_active_status})</span>
                </div>
            </div>
            <div style="text-align: right;">
                <span style="color: var(--text-muted); font-size: 0.78rem; font-weight:600;">가격 변동 방향 (Price Trend)</span>
                <div style="font-size:1.25rem; font-weight: 800; color: {direction_color}; margin-top:2px;">
                    {direction_arrow} ({active_change_str})
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ==========================================================================
    # TABS FOR CONTENT
    # ==========================================================================
    tab_chart, tab_simulator, tab_education = st.tabs([
        "📈 Interactive Charts (차트 분석)", 
        "🧮 Arbitrage Simulator (시뮬레이터)", 
        "📘 Arbitrage Guide (아비트리지 가이드)"
    ])

    # --------------------------------------------------------------------------
    # TAB 1: CHARTS
    # --------------------------------------------------------------------------
    with tab_chart:
        # Load histories
        with st.spinner("Loading historical price data..."):
            hist_kr = get_historical_data("000660.KS", period=historical_period)
            hist_adr = get_historical_data(adr_ticker_choice, period=historical_period)
            hist_fx = get_historical_data("USDKRW=X", period=historical_period)
            
        if hist_kr.empty or hist_adr.empty or hist_fx.empty:
            st.warning("⚠️ Could not load complete historical data for charting.")
        else:
            # Align indexes (Dates)
            hist_kr.index = hist_kr.index.strftime('%Y-%m-%d')
            hist_adr.index = hist_adr.index.strftime('%Y-%m-%d')
            hist_fx.index = hist_fx.index.strftime('%Y-%m-%d')
            
            all_dates = hist_kr.index.union(hist_adr.index).union(hist_fx.index)
            df_hist = pd.DataFrame(index=all_dates)
            
            df_hist['KRX_Price'] = hist_kr['Close']
            df_hist['ADR_Price_USD'] = hist_adr['Close']
            df_hist['FX_Rate'] = hist_fx['Close']
            
            # Forward fill missing data points (holidays, time-zone offsets)
            df_hist = df_hist.ffill().bfill()
            
            # Calculate daily premium
            df_hist['Implied_ADR_KRW'] = df_hist['ADR_Price_USD'] * adr_ratio * df_hist['FX_Rate']
            df_hist['Premium_Pct'] = ((df_hist['Implied_ADR_KRW'] / df_hist['KRX_Price']) - 1) * 100
            
            # Normalize for price comparisons (Initial point = 100)
            df_hist['KRX_Norm'] = (df_hist['KRX_Price'] / df_hist['KRX_Price'].iloc[0]) * 100
            df_hist['ADR_Norm'] = (df_hist['Implied_ADR_KRW'] / df_hist['Implied_ADR_KRW'].iloc[0]) * 100
            df_hist['FX_Norm'] = (df_hist['FX_Rate'] / df_hist['FX_Rate'].iloc[0]) * 100
            
            # Reset index for Plotly
            df_hist = df_hist.reset_index().rename(columns={'index': 'Date'})
            
            # Plotly Layout variables
            font_color = "#71717a" if not IS_DARK else "#a1a1aa"
            grid_color = "rgba(0,0,0,0.05)" if not IS_DARK else "rgba(255,255,255,0.05)"
            
            # 1. Historical Premium/Discount Chart
            st.markdown("""
            <div class="chart-wrap">
                <div class="chart-title">Historical Premium / Discount Volatility (아비트리지 프리미엄 추이)</div>
                <div class="chart-subtitle">Shows daily deviations from the Law of One Price (일물일가 괴리율)</div>
            """, unsafe_allow_html=True)
            
            fig_prem = go.Figure()
            # Premium line
            fig_prem.add_trace(go.Scatter(
                x=df_hist['Date'], y=df_hist['Premium_Pct'],
                mode='lines+markers',
                name='Premium (%)',
                line=dict(color='#2563eb', width=2),
                marker=dict(size=4),
                hovertemplate='Date: %{x}<br>Premium: %{y:+.2f}%<extra></extra>'
            ))
            # Reference line at 0 (Parity)
            fig_prem.add_trace(go.Scatter(
                x=df_hist['Date'], y=[0]*len(df_hist),
                mode='lines',
                name='Parity (적정가)',
                line=dict(color='#71717a', width=1, dash='dash'),
                showlegend=False
            ))
            
            fig_prem.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="DM Sans, sans-serif", color=font_color, size=11),
                margin=dict(l=40, r=20, t=10, b=20),
                height=300,
                xaxis=dict(gridcolor=grid_color, showgrid=True),
                yaxis=dict(gridcolor=grid_color, showgrid=True, title="Premium (%)", tickformat="+.1f%"),
                showlegend=False
            )
            
            st.plotly_chart(fig_prem, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)
            
            # 2. Comparative Performance Chart
            st.markdown("""
            <div class="chart-wrap">
                <div class="chart-title">Normalized Comparative Performance (정규화 가격 비교)</div>
                <div class="chart-subtitle">Baseline indexed at 100 for ordinary stock, ADR (in KRW terms), and exchange rate</div>
            """, unsafe_allow_html=True)
            
            fig_perf = go.Figure()
            fig_perf.add_trace(go.Scatter(
                x=df_hist['Date'], y=df_hist['KRX_Norm'],
                mode='lines',
                name='SK Hynix Ordinary (KRX)',
                line=dict(color='#ef4444' if IS_DARK else '#dc2626', width=2),
                hovertemplate='Ordinary: %{y:.1f}%<extra></extra>'
            ))
            fig_perf.add_trace(go.Scatter(
                x=df_hist['Date'], y=df_hist['ADR_Norm'],
                mode='lines',
                name='SK Hynix ADR (implied KRW)',
                line=dict(color='#22c55e' if IS_DARK else '#16a34a', width=2),
                hovertemplate='ADR (KRW): %{y:.1f}%<extra></extra>'
            ))
            fig_perf.add_trace(go.Scatter(
                x=df_hist['Date'], y=df_hist['FX_Norm'],
                mode='lines',
                name='USD/KRW FX Rate',
                line=dict(color='#f59e0b' if IS_DARK else '#d97706', width=1.5, dash='dot'),
                hovertemplate='FX Rate: %{y:.1f}%<extra></extra>'
            ))
            
            fig_perf.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="DM Sans, sans-serif", color=font_color, size=11),
                margin=dict(l=40, r=20, t=10, b=20),
                height=350,
                xaxis=dict(gridcolor=grid_color, showgrid=True),
                yaxis=dict(gridcolor=grid_color, showgrid=True, title="Indexed Performance (Base 100)"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig_perf, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Historical statistics table
            st.markdown("##### Historical Statistics (과거 통계 데이터)")
            
            avg_premium = df_hist['Premium_Pct'].mean()
            std_premium = df_hist['Premium_Pct'].std()
            max_premium = df_hist['Premium_Pct'].max()
            min_premium = df_hist['Premium_Pct'].min()
            
            table_rows = f"""
            <tr>
                <td><b>Average Premium (평균 프리미엄)</b></td>
                <td><span class="badge badge-blue">{avg_premium:+.2f}%</span></td>
                <td>평균적인 가격 괴리율입니다. 보통 0% 내외로 수렴합니다.</td>
            </tr>
            <tr>
                <td><b>Volatility of Premium (프리미엄 표준편차)</b></td>
                <td>{std_premium:.2f}%</td>
                <td>괴리율의 변동폭을 나타내며, 높을수록 아비트리지 기회가 자주 발생함을 뜻합니다.</td>
            </tr>
            <tr>
                <td><b>Maximum Premium (최대 할증)</b></td>
                <td><span class="badge badge-red">{max_premium:+.2f}%</span></td>
                <td>최근 조회 기간 중 ADR이 본주 대비 가장 고평가되었던 시점입니다.</td>
            </tr>
            <tr>
                <td><b>Minimum Premium (최대 할인)</b></td>
                <td><span class="badge badge-green">{min_premium:+.2f}%</span></td>
                <td>최근 조회 기간 중 ADR이 본주 대비 가장 저평가되었던 시점입니다.</td>
            </tr>
            """
            
            st.markdown(f"""
            <table class="data-table">
                <thead>
                    <tr>
                        <th style="width:30%;">Metric (지표)</th>
                        <th style="width:20%;">Value (값)</th>
                        <th>Description (설명)</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
            """, unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # TAB 2: ARBITRAGE SIMULATOR
    # --------------------------------------------------------------------------
    with tab_simulator:
        st.markdown("### 🧮 Arbitrage Trade Simulator (아비트리지 실거래 시뮬레이터)")
        st.write("본주와 ADR 간의 실제 거래 프로세스를 모델링하여 수수료, 환전 스프레드 및 Depositary Fee 등을 반영한 세후 순수익을 시뮬레이션합니다.")
        
        sim_col1, sim_col2 = st.columns([4, 6])
        
        with sim_col1:
            st.markdown("##### ⚙️ Setup Parameters (설정 변수)")
            capital_krw = st.number_input(
                "Trading Capital (투자금액, KRW)", 
                min_value=1_000_000, 
                max_value=10_000_000_000, 
                value=50_000_000, 
                step=5_000_000,
                format="%d"
            )
            
            st.markdown("###### Transaction Cost Estimates (수수료 추정)")
            # Standard K-market brokerage + tax
            brokerage_kr = st.slider("KRX Brokerage Fee (국내 수수료, %)", 0.0, 0.5, 0.015, step=0.005, format="%.3f%%")
            tax_kr = st.slider("KRX Transaction Tax (국내 거래세, %)", 0.0, 0.5, 0.18, step=0.01, format="%.2f%%")
            
            # US brokerage
            brokerage_us = st.slider("US Brokerage Fee (미국 수수료, %)", 0.0, 0.5, 0.05, step=0.01, format="%.2f%%")
            
            # FX Spread
            fx_spread = st.slider("FX Conversion Spread (환전 스프레드, %)", 0.0, 1.5, 0.20, step=0.05, format="%.2f%%")
            
            # ADR custodian fees (typically $0.05 per ADR for conversion)
            adr_conv_fee_per_share = st.number_input(
                "ADR Conversion Fee ($ per ADR)", 
                min_value=0.0, 
                max_value=1.0, 
                value=0.05, 
                step=0.01,
                format="%.2f"
            )

        with sim_col2:
            st.markdown("##### 📊 Simulation Result (시뮬레이션 결과)")
            
            # Determine flow direction
            # If Premium is positive (ADR > KRX): Buy KRX, convert and sell ADR
            # If Premium is negative (ADR < KRX): Buy ADR, convert and sell KRX
            
            # 1. KRX -> ADR (Premium > 0)
            # ------------------------------------------------
            # Korea Side Costs
            cost_brokerage_kr = capital_krw * (brokerage_kr / 100)
            cost_tax_kr = capital_krw * (tax_kr / 100) # Only when selling, but here we buy KRX. Wait, tax is charged only on sales in Korea!
            # Since we buy KRX, tax is 0. Tax is only when we sell KRX.
            # If we buy KRX and convert to ADR, we do not pay KRX transaction tax (tax is on sales).
            buy_power_krw = capital_krw - cost_brokerage_kr
            shares_bought = buy_power_krw / p_krx
            
            # Conversion to ADR
            adrs_converted = shares_bought * adr_ratio
            adr_fee_usd = adrs_converted * adr_conv_fee_per_share
            adr_fee_krw = adr_fee_usd * fx_rate
            
            # US Side Proceeds
            adr_value_usd = adrs_converted * p_adr
            cost_brokerage_us = adr_value_usd * (brokerage_us / 100)
            net_proceeds_usd = adr_value_usd - cost_brokerage_us - adr_fee_usd
            
            # Convert back to KRW
            # Pay FX spread when converting USD back to KRW
            fx_conversion_rate = fx_rate * (1 - fx_spread/100)
            net_proceeds_krw = net_proceeds_usd * fx_conversion_rate
            
            profit_krw_1 = net_proceeds_krw - capital_krw
            roi_1 = (profit_krw_1 / capital_krw) * 100
            
            # 2. ADR -> KRX (Premium < 0)
            # ------------------------------------------------
            # Convert KRW to USD (pay FX spread)
            fx_buy_rate = fx_rate * (1 + fx_spread/100)
            capital_usd = capital_krw / fx_buy_rate
            
            # US Side Costs & Buy ADR
            cost_brokerage_us_2 = capital_usd * (brokerage_us / 100)
            buy_power_usd = capital_usd - cost_brokerage_us_2
            adrs_bought = buy_power_usd / p_adr
            
            # Convert ADR to Ordinary (10 ADRs = 1 Share)
            shares_converted = adrs_bought / adr_ratio
            adr_fee_usd_2 = adrs_bought * adr_conv_fee_per_share
            adr_fee_krw_2 = adr_fee_usd_2 * fx_rate
            
            # KRX Side Proceeds
            krx_value_krw = shares_converted * p_krx
            cost_brokerage_kr_2 = krx_value_krw * (brokerage_kr / 100)
            cost_tax_kr_2 = krx_value_krw * (tax_kr / 100) # paying KRX tax because we sell ordinary shares in Korea
            net_proceeds_krw_2 = krx_value_krw - cost_brokerage_kr_2 - cost_tax_kr_2 - adr_fee_krw_2
            
            profit_krw_2 = net_proceeds_krw_2 - capital_krw
            roi_2 = (profit_krw_2 / capital_krw) * 100
            
            # Dynamically display the appropriate trade scenario based on premium
            if premium_pct >= 0:
                trade_direction = "Ordinary Stock (KOR) ➔ ADR (USA)"
                net_profit = profit_krw_1
                roi = roi_1
                total_fees_krw = cost_brokerage_kr + adr_fee_krw + (cost_brokerage_us * fx_rate) + (capital_krw * (fx_spread/100))
                
                # Breakdown text
                steps_html = f"""
                <div style="font-size:0.82rem; line-height: 1.6;">
                    1. <b>국내주식 매수</b>: {capital_krw:,.0f} KRW으로 SK하이닉스 <b>{shares_bought:.1f}주</b> 매수 (수수료: {cost_brokerage_kr:,.0f} KRW)<br>
                    2. <b>ADR 전환 요청</b>: {shares_bought:.1f}주를 ADR로 전환하여 <b>{adrs_converted:.1f} ADR</b> 취득 (Depositary fee: ${adr_fee_usd:.2f} / {adr_fee_krw:,.0f} KRW)<br>
                    3. <b>미국주식 매도</b>: NASDAQ에서 {adrs_converted:.1f} ADR을 주당 ${p_adr:.2f}에 매도하여 총 <b>${adr_value_usd:,.2f}</b> 수취 (수수료: ${cost_brokerage_us:.2f})<br>
                    4. <b>원화 환전</b>: 수취한 달러를 원화로 환전 (우대 환율 스프레드 {fx_spread}% 적용) ➔ 최종 수령액: <b>{net_proceeds_krw:,.0f} KRW</b>
                </div>
                """
            else:
                trade_direction = "ADR (USA) ➔ Ordinary Stock (KOR)"
                net_profit = profit_krw_2
                roi = roi_2
                total_fees_krw = (cost_brokerage_us_2 * fx_rate) + adr_fee_krw_2 + cost_brokerage_kr_2 + cost_tax_kr_2 + (capital_krw * (fx_spread/100))
                
                steps_html = f"""
                <div style="font-size:0.82rem; line-height: 1.6;">
                    1. <b>달러 환전</b>: {capital_krw:,.0f} KRW을 달러로 환전 (환율 스프레드 {fx_spread}% 적용) ➔ <b>${capital_usd:,.2f} USD</b> 취득<br>
                    2. <b>ADR 매수</b>: NASDAQ에서 SK하이닉스 ADR <b>{adrs_bought:.1f} ADR</b> 매수 (수수료: ${cost_brokerage_us_2:.2f})<br>
                    3. <b>본주 전환 요청</b>: {adrs_bought:.1f} ADR을 본주로 전환하여 <b>{shares_converted:.1f}주</b> 취득 (Depositary fee: ${adr_fee_usd_2:.2f} / {adr_fee_krw_2:,.0f} KRW)<br>
                    4. <b>국내주식 매도</b>: KRX에서 {shares_converted:.1f}주를 주당 {p_krx:,.0f} KRW에 매도 (국내수수료: {cost_brokerage_kr_2:,.0f} KRW, 거래세: {cost_tax_kr_2:,.0f} KRW) ➔ 최종 수령액: <b>{net_proceeds_krw_2:,.0f} KRW</b>
                </div>
                """
                
            badge_color = "badge-green" if net_profit > 0 else "badge-red"
            st.markdown(f"""
            <div style="background: var(--bg-subtle); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.25rem 1.4rem; box-shadow: var(--shadow); margin-bottom:1rem;">
                <div style="font-size:0.75rem; color:var(--text-muted); font-weight:600; text-transform:uppercase; letter-spacing:0.05em;">Recommended Arbitrage Direction</div>
                <div style="font-size:1.2rem; font-weight:800; color:var(--text); margin-top:2px; margin-bottom: 0.8rem;">
                    {trade_direction}
                </div>
                
                <table style="width:100%; font-size:0.85rem; border-collapse: collapse;">
                    <tr style="border-bottom: 1px solid var(--border-subtle);">
                        <td style="padding: 0.5rem 0; color:var(--text-muted);">총 투자금액 (Capital)</td>
                        <td style="padding: 0.5rem 0; text-align:right; font-weight:600;">{capital_krw:,.0f} KRW</td>
                    </tr>
                    <tr style="border-bottom: 1px solid var(--border-subtle);">
                        <td style="padding: 0.5rem 0; color:var(--text-muted);">예상 총 비용 (Total Estimated Costs)</td>
                        <td style="padding: 0.5rem 0; text-align:right; font-weight:600; color:var(--red);">{total_fees_krw:,.0f} KRW</td>
                    </tr>
                    <tr style="border-bottom: 1px solid var(--border-subtle);">
                        <td style="padding: 0.5rem 0; color:var(--text-muted);">실질 프리미엄 괴리율 (Raw Premium)</td>
                        <td style="padding: 0.5rem 0; text-align:right; font-weight:600; color:var(--accent);">{premium_pct:+.2f}%</td>
                    </tr>
                    <tr style="border-bottom: 1px solid var(--border-subtle);">
                        <td style="padding: 0.5rem 0; color:var(--text-muted);">수수료 차감 후 순수익 (Net Profit)</td>
                        <td style="padding: 0.5rem 0; text-align:right; font-weight:700;"><span class="badge {badge_color}" style="font-size:0.85rem; padding: 3px 10px;">{net_profit:+,.0f} KRW</span></td>
                    </tr>
                    <tr>
                        <td style="padding: 0.5rem 0; color:var(--text-muted);">수수료 차감 후 수익률 (Net ROI)</td>
                        <td style="padding: 0.5rem 0; text-align:right; font-weight:700; color: {'var(--green)' if roi > 0 else 'var(--red)'};">{roi:+.3f}%</td>
                    </tr>
                </table>
            </div>
            
            <div style="background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem 1.2rem;">
                <div style="font-size:0.78rem; font-weight:600; color:var(--text); margin-bottom: 0.5rem; text-transform:uppercase;">Step-by-step Execution Process (거래 단계별 상세 내역)</div>
                {steps_html}
            </div>
            """, unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # TAB 3: EDUCATION
    # --------------------------------------------------------------------------
    with tab_education:
        st.markdown("### 📘 Ordinary Stock & ADR Arbitrage Theory (아비트리지 이론 및 유의사항)")
        
        st.markdown("""
        #### 1. 일물일가의 법칙 (Law of One Price)
        동일한 가치를 가지는 자산은 어떤 시장에서 거래되든 그 가격이 같아야 한다는 금융의 기본 법칙입니다. 
        SK하이닉스 본주(KRX: 000660)와 미국 NASDAQ에 상장된 ADR(티커: SKHY)은 전환 비율(1:10)에 따라 동일한 기초 자산을 나타내므로 본주 가격에 원/달러 환율과 전환 비율을 적용한 **적정 가치(Implied Value)**가 ADR 실제 시장 가격과 일치해야 합니다.

        $$Implied\\ ADR\\ (KRW) = ADR\\ Price\\ (USD) \\times Ratio\\ (10) \\times USD/KRW\\ Exchange\\ Rate$$

        이 적정 가치와 본주 가격 간에 괴리가 발생하는 비율을 **프리미엄(Premium) 또는 할인(Discount)**이라고 부릅니다.

        #### 2. 실거래 장벽 및 리스크 (Trading Realities & Risks)
        이론상으로는 괴리율이 존재할 때 즉시 무위험 차익거래(Arbitrage)가 가능하지만, 실제 거래에서는 다음과 같은 제약사항이 따릅니다.
        
        *   **환율 변동 리스크 (Currency Risk)**: 거래가 완전히 청산되는 동안 원/달러 환율이 불리하게 변동할 수 있습니다.
        *   **시간차 리스크 (Execution Delay)**: 한국 시장과 미국 시장은 시차(Timezone Difference)로 인해 동시 세션 운영 시간이 없습니다. 한국 주식을 매입하여 미국에 ADR로 등록 및 인도하는 데 보통 수일(T+2 이상)이 소요됩니다. 이 기간 동안 주가가 하락하면 손실을 볼 수 있습니다.
        *   **전환 비용 (Conversion Fees)**: Depositary Bank(보관은행)인 Citibank 등은 주식-ADR 전환 및 취소 시 ADR당 보통 **$0.05** 수준의 보관수수료(Custodian Fee)를 청구합니다.
        *   **법적 제약 (Regulatory Constraints)**: 대한민국의 외국환거래법(Foreign Exchange Transactions Act)에 따라 개인투자자의 무허가 해외 자본 유출 및 차익 거래 목적의 해외 외환 송금은 금액 제한 및 신고 의무가 엄격하게 적용됩니다.
        *   **대차 거래 비용 (Stock Borrowing Costs)**: 시간차를 제거하기 위해 동시에 한쪽은 공매도(Short-selling)를 치고 다른 한쪽은 매수를 진행하는 방식을 채택하는 경우, 공매도에 따른 주식 대차 이자 비용이 발생합니다.
        """)

# ==============================================================================
# FOOTER
# ==============================================================================
st.markdown("---")
st.markdown(
    "<div style='text-align: center; font-size: 0.72rem; color: #71717a; padding: 10px 0;'>"
    "SK Hynix Arbitrage Dashboard Pro • Designed with premium zinc aesthetics. "
    "All financial analysis yields indicative estimations only. Verified local time: 2026-07-23."
    "</div>", 
    unsafe_allow_html=True
)

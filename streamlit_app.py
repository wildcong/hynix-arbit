import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import pytz
import requests
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==============================================================================
# 페이지 설정 및 테마 초기화
# ==============================================================================
st.set_page_config(
    page_title="SK하이닉스 아비트리지 허브",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "theme" not in st.session_state:
    st.session_state.theme = "light"

def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

IS_DARK = st.session_state.theme == "dark"

# ==============================================================================
# CSS 디자인 시스템 (Zinc 프리미엄 테마)
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
    
    /* Streamlit 기본 헤더 및 푸터 숨기기 */
    header[data-testid="stHeader"], [data-testid="stToolbar"],
    [data-testid="stDecoration"], [data-testid="stStatusWidget"], .stDeployButton {{
        display: none !important;
    }}
    
    /* 앱 전반 스타일 정의 */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main, .block-container, section[data-testid="stMain"] {{
        background-color: var(--bg) !important;
        color: var(--text) !important;
        font-family: 'DM Sans', -apple-system, sans-serif !important;
    }}
    .block-container {{
        padding: 1.5rem 2rem 2rem !important;
        max-width: 1360px !important;
    }}
    
    /* 탭(Pill 스타일) 커스텀 */
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
    
    /* 지표 카드(KPI) 스타일 */
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
    
    /* 차트 박스 스타일 */
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
    
    /* 데이터 테이블 스타일 */
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
    
    /* 상태 배지 스타일 */
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
    
    /* 브랜드 헤더 */
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
    
    /* 사이드바 커스텀 */
    section[data-testid="stSidebar"] {{
        background-color: var(--bg-subtle) !important;
        border-right: 1px solid var(--border) !important;
    }}
    section[data-testid="stSidebar"] .stButton button {{
        background-color: var(--card) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
    }}
    
    /* 입력 필드 커스텀 */
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
# 데이터 엔진 (한국투자증권 KIS API & yfinance)
# ==============================================================================

# 1. 한국투자증권 Access Token 발급 및 공유 캐싱
@st.cache_data(ttl=86000)
def fetch_kis_access_token(app_key, app_secret, url_base):
    """
    한국투자증권 OAuth2 Token 발급 함수.
    Streamlit 전역 캐시(ttl=86000초, 약 24시간)를 적용하여 모든 세션에서 1개의 토큰을 공유합니다.
    """
    url = f"{url_base}/oauth2/tokenP"
    headers = {"content-type": "application/json"}
    body = {
        "grant_type": "client_credentials",
        "appkey": app_key,
        "appsecret": app_secret
    }
    try:
        res = requests.post(url, headers=headers, data=json.dumps(body), timeout=10)
        if res.status_code == 200:
            token = res.json().get("access_token")
            # 콘솔에 토큰 새로 발급됨을 기록
            print(f"[{datetime.datetime.now()}] KIS API Access Token 새로 발급 완료.")
            return token
    except Exception as e:
        print(f"KIS API 토큰 발급 에러: {e}")
    return None

# 2. 한국투자증권 국내주식 실시간 시세 조회
@st.cache_data(ttl=10, show_spinner=False)
def get_realtime_price_kis(ticker, access_token, app_key, app_secret, url_base):
    """
    한국투자증권 OpenAPI 국내주식 실시간 주가 조회 함수 (캐싱 10초).
    """
    headers = {
        "content-type": "application/json; charset=utf-8", 
        "authorization": f"Bearer {access_token}",
        "appkey": app_key,
        "appsecret": app_secret, 
        "tr_id": "FHKST01010100", # 주식 현재가 시세 tr_id
        "custtype": "P"
    }
    params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": ticker}
    url = f"{url_base}/uapi/domestic-stock/v1/quotations/inquire-price"
    try:
        res = requests.get(url, headers=headers, params=params, timeout=5)
        if res.status_code == 200:
            res_json = res.json()
            if 'output' in res_json:
                output = res_json['output']
                return {
                    "price": float(output.get('stck_prpr', 0)),
                    "diff": float(output.get('prdy_vrss', 0)),
                    "rate": float(output.get('prdy_ctrt', 0.0))
                }
    except Exception as e:
        print(f"KIS API 실시간 주가 조회 에러 ({ticker}): {e}")
    return None

# 3. yfinance 롤백/실시간 시세 조회 함수
@st.cache_data(ttl=15)
def get_live_quote(ticker_symbol):
    """
    yfinance를 통한 실시간 가격 조회 함수 (15초 캐시).
    """
    ticker = yf.Ticker(ticker_symbol)
    price = None
    prev_close = None
    currency = "USD"
    
    # 1안: fast_info 사용
    try:
        info = ticker.fast_info
        price = info.get('lastPrice') or info.get('last_price')
        prev_close = info.get('previousClose') or info.get('previous_close')
        currency = info.get('currency', currency)
    except Exception:
        pass
        
    # 2안: history 사용
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
            
    # 3안: 일반 info 딕셔너리 사용
    if price is None:
        try:
            info = ticker.info
            price = info.get('regularMarketPrice') or info.get('currentPrice')
            prev_close = info.get('regularMarketPreviousClose') or info.get('previousClose')
            currency = info.get('currency', currency)
        except Exception:
            pass
            
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

# 4. 과거 역사적 시세 데이터 가져오기
@st.cache_data(ttl=3600)
def get_historical_data(ticker_symbol, period="1mo"):
    """
    과거 차트 그리기를 위한 역사적 주가 데이터 조회 함수 (3600초 캐시).
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period=period)
        if not df.empty:
            return df[['Close']]
    except Exception as e:
        st.warning(f"{ticker_symbol}의 역사적 데이터를 불러오는 중 오류 발생: {e}")
    return pd.DataFrame()

# 5. 거래소 운영 상태 분석 및 한국/미국 시간대 트래커
def get_market_status():
    """
    TimeZone을 고려한 거래소 거래 시간 판별 함수.
    한국(KST): 월~금, 09:00 ~ 15:30 정규장.
    미국(EST/EDT): 월~금, 04:00~09:30 프리마켓, 09:30~16:00 정규장, 16:00~20:00 애프터마켓.
    """
    kst = pytz.timezone('Asia/Seoul')
    est = pytz.timezone('America/New_York')
    
    now_utc = datetime.datetime.now(pytz.utc)
    now_kst = now_utc.astimezone(kst)
    now_est = now_utc.astimezone(est)
    
    # 한국 장 상태 분석
    k_weekday = now_kst.weekday()
    k_time = now_kst.time()
    k_open = datetime.time(9, 0)
    k_close = datetime.time(15, 30)
    
    if k_weekday >= 5:
        k_status = "주말 휴장"
        k_status_class = "badge-red"
    elif k_open <= k_time <= k_close:
        k_status = "정규장 진행 중"
        k_status_class = "badge-green"
    else:
        k_status = "장마감"
        k_status_class = "badge-red"
        
    # 미국 장 상태 분석
    u_weekday = now_est.weekday()
    u_time = now_est.time()
    u_pre = datetime.time(4, 0)
    u_reg_open = datetime.time(9, 30)
    u_reg_close = datetime.time(16, 0)
    u_post_close = datetime.time(20, 0)
    
    if u_weekday >= 5:
        u_status = "주말 휴장"
        u_status_class = "badge-red"
    elif u_reg_open <= u_time <= u_reg_close:
        u_status = "정규장 진행 중"
        u_status_class = "badge-green"
    elif u_pre <= u_time < u_reg_open:
        u_status = "프리마켓 진행 중"
        u_status_class = "badge-amber"
    elif u_reg_close < u_time <= u_post_close:
        u_status = "애프터마켓 진행 중"
        u_status_class = "badge-amber"
    else:
        u_status = "장마감"
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
# 사이드바 컨트롤 영역
# ==============================================================================
st.sidebar.markdown("""
<div class="brand">
    <span class="brand-name">Hynix 아비트리지</span>
    <span class="brand-badge">PRO</span>
</div>
""", unsafe_allow_html=True)
st.sidebar.write("")

# 1. 한국투자증권 API Key 조회 (secrets.toml에서 비보이지 않게 로드)
kis_app_key = ""
kis_app_secret = ""
try:
    kis_app_key = st.secrets.get("KIS_APP_KEY", "")
    kis_app_secret = st.secrets.get("KIS_APP_SECRET", "")
except Exception:
    pass

kis_url_base = "https://openapi.koreainvestment.com:9443"
st.sidebar.write("---")

# 2. 거래 자산 설정
st.sidebar.subheader("⚙️ 거래 자산 설정")
adr_ticker_choice = st.sidebar.text_input(
    "미국 ADR 티커 입력",
    value="SKHY",
    help="NASDAQ 공식 ADR 티커인 SKHY를 기본으로 사용합니다. 야후 파이낸스에 등록된 유효한 티커만 연동됩니다."
).upper()

adr_ratio = st.sidebar.number_input(
    "ADR 전환 비율 (1주당 ADR 수량)",
    min_value=0.01,
    max_value=100.0,
    value=10.0,
    step=1.0,
    help="SK하이닉스 본주 1주가 대체하는 미국 ADR의 수량입니다. 공식 비율은 1:10 (본주 1주 = 10 ADR) 입니다."
)

historical_period = st.sidebar.selectbox(
    "차트 조회 기간",
    ["5d", "1mo", "3mo", "6mo", "1y"],
    index=1
)

st.sidebar.write("---")

# 수동 새로고침 버튼
if st.sidebar.button("🔄 강제 새로고침 (데이터 갱신)", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# 테마 토글 버튼
theme_label = "☀️ 라이트 테마 전환" if IS_DARK else "🌙 다크 테마 전환"
st.sidebar.button(theme_label, on_click=toggle_theme, use_container_width=True)

st.sidebar.markdown(f"""
<div style="font-size:0.72rem; color: #71717a; margin-top:20px;">
    실시간 시세: 한국투자증권 API / yfinance<br>
    Access Token 공유 캐시: 적용 완료<br>
    기준 표준시: KST (서울)
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 실시간 데이터 수집 및 예외 처리
# ==============================================================================
with st.spinner("시장 데이터 로딩 중..."):
    # 1. 한국투자증권 실시간 주가 수집 시도 (K-Market)
    kis_active = False
    kis_price_data = None
    
    if kis_app_key and kis_app_secret:
        access_token = fetch_kis_access_token(kis_app_key, kis_app_secret, kis_url_base)
        if access_token:
            # SK하이닉스 국내주식 종목코드 '000660'
            kis_price_data = get_realtime_price_kis("000660", access_token, kis_app_key, kis_app_secret, kis_url_base)
            if kis_price_data and kis_price_data['price'] > 0:
                kis_active = True
                
    # 2. 국내주식 시세 딕셔너리 준비
    if kis_active and kis_price_data:
        krx_price = kis_price_data['price']
        krx_change_rate = kis_price_data['rate']
        krx_prev_close = krx_price - kis_price_data['diff']
        krx_data = {
            "ticker": "000660 (한국투자 OpenAPI)",
            "price": krx_price,
            "prev_close": krx_prev_close,
            "currency": "KRW",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    else:
        # KIS 실패 시 yfinance fallback 적용
        krx_data = get_live_quote("000660.KS")
        krx_data["ticker"] = "000660.KS (yfinance 지연)"
        
    # 3. 미국 ADR 및 환율 정보 조회 (yfinance 활용)
    adr_data = get_live_quote(adr_ticker_choice)
    fx_data = get_live_quote("USDKRW=X")
    
    # 데이터 유효성 검사
    data_valid = (
        krx_data['price'] is not None and 
        adr_data['price'] is not None and 
        fx_data['price'] is not None
    )

# ==============================================================================
# 메인화면 레이아웃 구성
# ==============================================================================

# 타이틀 헤더 영역
t_col1, t_col2 = st.columns([7, 3])
with t_col1:
    st.markdown("""
    <h1 style="font-size:2.0rem; font-weight:800; letter-spacing:-0.05em; margin: 0 0 5px 0;">
        SK하이닉스 아비트리지 모니터링 대시보드
    </h1>
    <p style="font-size:0.85rem; color:#71717a; margin: 0;">
        일물일가(Law of One Price) 원칙에 기반한 본주와 미국 ADR 실시간 프리미엄 괴리 모니터링
    </p>
    """, unsafe_allow_html=True)

# 시간대 및 시장 현황 컴포넌트
m_status = get_market_status()
with t_col2:
    st.markdown(f"""
    <div style="background: var(--card); border: 1px solid var(--border); padding: 0.6rem 0.9rem; border-radius: var(--radius); font-size: 0.76rem; line-height: 1.45;">
        <div>🇰🇷 <b>서울 (KST):</b> <span style="font-family: monospace;">{m_status['kst_time']}</span> <span class="badge {m_status['k_status_class']}">{m_status['k_status']}</span></div>
        <div style="margin-top:4px;">🇺🇸 <b>뉴욕 (EST/EDT):</b> <span style="font-family: monospace;">{m_status['est_time']}</span> <span class="badge {m_status['u_status_class']}">{m_status['u_status']}</span></div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

if not data_valid:
    st.error("⚠️ 실시간 금융 데이터를 가져오는데 실패했습니다. 네트워크 상태를 확인하거나 잠시 후 새로고침을 진행해 주세요.")
    st.json({"국내주식": krx_data, "미국ADR": adr_data, "환율": fx_data})
else:
    # 핵심 데이터 변수 바인딩
    p_krx = krx_data['price']
    p_adr = adr_data['price']
    fx_rate = fx_data['price']
    
    # 상승률 계산
    if kis_active:
        krx_pct = krx_change_rate
        sign = "+" if krx_pct >= 0 else ""
        krx_pct_str = f"{sign}{krx_pct:.2f}%"
    else:
        krx_pct, krx_pct_str = calculate_change(p_krx, krx_data['prev_close'])
        
    adr_pct, adr_pct_str = calculate_change(p_adr, adr_data['prev_close'])
    fx_pct, fx_pct_str = calculate_change(fx_rate, fx_data['prev_close'])
    
    # 1본주당 미국 ADR 내재 가치 환산 (1본주 = adr_ratio * ADR)
    implied_adr_krw = adr_ratio * p_adr * fx_rate
    
    # 아비트리지 프리미엄 / 괴리율 산출
    premium_pct = ((implied_adr_krw / p_krx) - 1) * 100
    
    # 프리미엄 상태 분류
    if premium_pct > 0.5:
        prem_status = "ADR 고평가 (할증)"
        prem_class = "delta-down" # 본주 매수, ADR 매도 (ADR 매도 시 순익)
        prem_badge_class = "badge-red"
    elif premium_pct < -0.5:
        prem_status = "ADR 저평가 (할인)"
        prem_class = "delta-up" # ADR 매수, 본주 매도
        prem_badge_class = "badge-green"
    else:
        prem_status = "패리티 도달 (적정)"
        prem_class = "delta-warn"
        prem_badge_class = "badge-blue"

    # ==========================================================================
    # 실시간 지표 카드 행 (4열 구성)
    # ==========================================================================
    kpi_cols = st.columns(4)
    
    # 1. 국내 본주 주가
    with kpi_cols[0]:
        delta_type = "up" if krx_pct >= 0 else "down"
        source_label = "OpenAPI 실시간" if kis_active else "yfinance 지연"
        metric_card(
            label=f"SK하이닉스 본주 ({source_label})",
            value=f"{p_krx:,.0f} KRW",
            delta=krx_pct_str,
            delta_type=delta_type
        )
        
    # 2. 미국 ADR 주가
    with kpi_cols[1]:
        delta_type = "up" if adr_pct >= 0 else "down"
        metric_card(
            label=f"미국 ADR ({adr_ticker_choice})",
            value=f"${p_adr:.2f} USD",
            delta=adr_pct_str,
            delta_type=delta_type
        )
        
    # 3. 원/달러 기준환율
    with kpi_cols[2]:
        delta_type = "up" if fx_pct >= 0 else "down"
        metric_card(
            label="원/달러 환율 (USDKRW)",
            value=f"{fx_rate:,.2f} ₩",
            delta=fx_pct_str,
            delta_type=delta_type
        )
        
    # 4. 차익 프리미엄
    with kpi_cols[3]:
        delta_type = "down" if premium_pct > 0.5 else ("up" if premium_pct < -0.5 else "warn")
        metric_card(
            label="ADR 프리미엄 / 괴리율",
            value=f"{premium_pct:+.2f}%",
            delta=prem_status,
            delta_type=delta_type
        )

    # ==========================================================================
    # 실시간 주도 시장 및 트렌드
    # ==========================================================================
    kst_now = m_status['kst_raw']
    k_status = m_status['k_status']
    u_status = m_status['u_status']
    
    # 기본값 설정
    recently_active = "한국 주식시장 (KRX)"
    recently_active_status = "🔴 장마감"
    active_change_str = krx_pct_str
    active_change_val = krx_pct
    
    if k_status == "정규장 진행 중":
        recently_active = "한국 주식시장 (KRX)"
        recently_active_status = "🟢 정규장 거래 중"
        active_change_str = krx_pct_str
        active_change_val = krx_pct
    elif u_status == "정규장 진행 중":
        recently_active = "미국 주식시장 (NASDAQ)"
        recently_active_status = "🟢 정규장 거래 중"
        active_change_str = adr_pct_str
        active_change_val = adr_pct
    elif u_status in ["프리마켓 진행 중", "애프터마켓 진행 중"]:
        recently_active = "미국 주식시장 (NASDAQ)"
        recently_active_status = f"🟡 {u_status}"
        active_change_str = adr_pct_str
        active_change_val = adr_pct
    else:
        # 양대 마켓 모두 닫혀 있는 경우 (평일 밤/새벽 혹은 주말)
        # 한국시간 기준 주말(토, 일) 및 월요일 아침 9시 이전에는 가장 최근에 거래된 시장이 금요일 밤 미국 시장임.
        k_weekday = kst_now.weekday() # 0=월, 5=토, 6=일
        k_hour = kst_now.hour
        
        is_us_last = False
        if k_weekday == 5: # 토요일
            is_us_last = True
        elif k_weekday == 6: # 일요일
            is_us_last = True
        elif k_weekday == 0: # 월요일
            if k_hour < 9:
                is_us_last = True
        else: # 화~금요일
            # 평일 오전 5시(미국 장마감) ~ 오전 9시(한국 개장) 사이에는 미국 장이 직전 장임.
            if k_hour < 9:
                is_us_last = True
                
        if is_us_last:
            recently_active = "미국 주식시장 (NASDAQ)"
            recently_active_status = "🔴 주말 휴장" if k_weekday in [5, 6] or (k_weekday == 0 and k_hour < 9) else "🔴 장마감 (최근 활성)"
            active_change_str = adr_pct_str
            active_change_val = adr_pct
        else:
            recently_active = "한국 주식시장 (KRX)"
            recently_active_status = "🔴 주말 휴장" if k_status == "주말 휴장" else "🔴 장마감 (최근 활성)"
            active_change_str = krx_pct_str
            active_change_val = krx_pct

    direction_arrow = "📈 상승세 주도" if active_change_val > 0 else ("📉 하락세 주도" if active_change_val < 0 else "➡️ 보합")
    direction_color = "var(--green)" if active_change_val > 0 else ("var(--red)" if active_change_val < 0 else "var(--text-muted)")
    
    st.markdown(f"""
    <div style="background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 0.9rem 1.25rem; margin-bottom: 1.25rem; box-shadow: var(--shadow);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
            <div>
                <span style="color: var(--text-muted); font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">최근 거래된 시장 주도력 (Market Momentum)</span>
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
    # 컨텐츠 영역 탭 구조
    # ==========================================================================
    tab_chart, tab_simulator, tab_education = st.tabs([
        "📈 차트 분석 (Interactive Charts)", 
        "🧮 아비트리지 시뮬레이터 (Simulator)", 
        "📘 차익거래 이론 및 가이드 (Guide)"
    ])

    # --------------------------------------------------------------------------
    # 탭 1: 차트 분석
    # --------------------------------------------------------------------------
    with tab_chart:
        with st.spinner("역사적 추세 데이터 불러오는 중..."):
            hist_kr = get_historical_data("000660.KS", period=historical_period)
            hist_adr = get_historical_data(adr_ticker_choice, period=historical_period)
            hist_fx = get_historical_data("USDKRW=X", period=historical_period)
            
        if hist_kr.empty or hist_adr.empty or hist_fx.empty:
            st.warning("⚠️ 역사적 차트를 그리기 위한 일부 데이터가 부족합니다.")
        else:
            # 날짜 정렬 작업
            hist_kr.index = hist_kr.index.strftime('%Y-%m-%d')
            hist_adr.index = hist_adr.index.strftime('%Y-%m-%d')
            hist_fx.index = hist_fx.index.strftime('%Y-%m-%d')
            
            all_dates = hist_kr.index.union(hist_adr.index).union(hist_fx.index)
            df_hist = pd.DataFrame(index=all_dates)
            
            df_hist['KRX_Price'] = hist_kr['Close']
            df_hist['ADR_Price_USD'] = hist_adr['Close']
            df_hist['FX_Rate'] = hist_fx['Close']
            
            # 주말/시차로 인한 결측치 전방 채우기(Forward Fill) 적용
            df_hist = df_hist.ffill().bfill()
            
            # 일별 내재 ADR 및 프리미엄 계산
            df_hist['Implied_ADR_KRW'] = df_hist['ADR_Price_USD'] * adr_ratio * df_hist['FX_Rate']
            df_hist['Premium_Pct'] = ((df_hist['Implied_ADR_KRW'] / df_hist['KRX_Price']) - 1) * 100
            
            # 가격 정규화 (최초 시점 = 100 기준 수익률 비교용)
            df_hist['KRX_Norm'] = (df_hist['KRX_Price'] / df_hist['KRX_Price'].iloc[0]) * 100
            df_hist['ADR_Norm'] = (df_hist['Implied_ADR_KRW'] / df_hist['Implied_ADR_KRW'].iloc[0]) * 100
            df_hist['FX_Norm'] = (df_hist['FX_Rate'] / df_hist['FX_Rate'].iloc[0]) * 100
            
            df_hist = df_hist.reset_index().rename(columns={'index': 'Date'})
            
            font_color = "#71717a" if not IS_DARK else "#a1a1aa"
            grid_color = "rgba(0,0,0,0.05)" if not IS_DARK else "rgba(255,255,255,0.05)"
            
            # 차트 1: 아비트리지 프리미엄 추이
            st.markdown("""
            <div class="chart-wrap">
                <div class="chart-title">역사적 프리미엄 / 괴리율 추이 (Premium Volatility)</div>
                <div class="chart-subtitle">본주 대비 미국 ADR 주가의 일별 괴리 정도 (%)</div>
            """, unsafe_allow_html=True)
            
            fig_prem = go.Figure()
            fig_prem.add_trace(go.Scatter(
                x=df_hist['Date'], y=df_hist['Premium_Pct'],
                mode='lines+markers',
                name='프리미엄 (%)',
                line=dict(color='#2563eb', width=2),
                marker=dict(size=4),
                hovertemplate='날짜: %{x}<br>괴리율: %{y:+.2f}%<extra></extra>'
            ))
            fig_prem.add_trace(go.Scatter(
                x=df_hist['Date'], y=[0]*len(df_hist),
                mode='lines',
                name='패리티 (Parity)',
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
                yaxis=dict(gridcolor=grid_color, showgrid=True, title="프리미엄 (%)", tickformat="+.1f%"),
                showlegend=False
            )
            
            st.plotly_chart(fig_prem, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)
            
            # 차트 2: 정규화 주가 비교
            st.markdown("""
            <div class="chart-wrap">
                <div class="chart-title">자산별 정규화 가격 변동 추이 (Normalized Performance)</div>
                <div class="chart-subtitle">조회 시작 시점의 가치를 100으로 기준한 상대 변동폭</div>
            """, unsafe_allow_html=True)
            
            fig_perf = go.Figure()
            fig_perf.add_trace(go.Scatter(
                x=df_hist['Date'], y=df_hist['KRX_Norm'],
                mode='lines',
                name='SK하이닉스 본주 (KRX)',
                line=dict(color='#ef4444' if IS_DARK else '#dc2626', width=2),
                hovertemplate='본주: %{y:.1f}%<extra></extra>'
            ))
            fig_perf.add_trace(go.Scatter(
                x=df_hist['Date'], y=df_hist['ADR_Norm'],
                mode='lines',
                name='SK하이닉스 ADR (원화 환산)',
                line=dict(color='#22c55e' if IS_DARK else '#16a34a', width=2),
                hovertemplate='ADR (원화): %{y:.1f}%<extra></extra>'
            ))
            fig_perf.add_trace(go.Scatter(
                x=df_hist['Date'], y=df_hist['FX_Norm'],
                mode='lines',
                name='원/달러 환율',
                line=dict(color='#f59e0b' if IS_DARK else '#d97706', width=1.5, dash='dot'),
                hovertemplate='환율 변동: %{y:.1f}%<extra></extra>'
            ))
            
            fig_perf.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="DM Sans, sans-serif", color=font_color, size=11),
                margin=dict(l=40, r=20, t=10, b=20),
                height=350,
                xaxis=dict(gridcolor=grid_color, showgrid=True),
                yaxis=dict(gridcolor=grid_color, showgrid=True, title="정규화 지수 (Base 100)"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig_perf, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)
            
            # 과거 통계 데이터 테이블
            st.markdown("##### 과거 괴리율 통계 데이터 (Historical Statistics)")
            
            avg_premium = df_hist['Premium_Pct'].mean()
            std_premium = df_hist['Premium_Pct'].std()
            max_premium = df_hist['Premium_Pct'].max()
            min_premium = df_hist['Premium_Pct'].min()
            
            table_rows = (
                f'<tr><td><b>평균 프리미엄 (Average Premium)</b></td><td><span class="badge badge-blue">{avg_premium:+.2f}%</span></td><td>조회 기간의 평균 괴리율입니다. 보통 장기적으로 0% 내외로 수렴합니다.</td></tr>'
                f'<tr><td><b>프리미엄 표준편차 (Volatility of Premium)</b></td><td>{std_premium:.2f}%</td><td>괴리율이 평균 대비 변동한 범위입니다. 높을수록 아비트리지(차익) 거래 진입/청산 기회가 잦음을 의미합니다.</td></tr>'
                f'<tr><td><b>최대 프리미엄 할증 (Max Overvaluation)</b></td><td><span class="badge badge-red">{max_premium:+.2f}%</span></td><td>ADR이 본주 대비 역사적으로 가장 높은 할증(비싸게) 거래되었던 시점입니다.</td></tr>'
                f'<tr><td><b>최대 프리미엄 할인 (Max Undervaluation)</b></td><td><span class="badge badge-green">{min_premium:+.2f}%</span></td><td>ADR이 본주 대비 역사적으로 가장 높은 할인(싸게) 거래되었던 시점입니다.</td></tr>'
            )
            
            html_table = (
                f'<table class="data-table">'
                f'<thead><tr><th style="width:30%;">통계 지표</th><th style="width:20%;">수치</th><th>지표 설명</th></tr></thead>'
                f'<tbody>{table_rows}</tbody>'
                f'</table>'
            )
            st.markdown(html_table, unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # 탭 2: 아비트리지 시뮬레이터
    # --------------------------------------------------------------------------
    with tab_simulator:
        st.markdown("### 🧮 아비트리지 거래 시뮬레이터 (Arbitrage Simulator)")
        st.write("본주와 ADR 간의 실제 교환 및 거래 프로세스를 바탕으로 제반 수수료, 환전 우대율 및 주식 전환수수료를 산출해 순수익을 모델링합니다.")
        
        sim_col1, sim_col2 = st.columns([4, 6])
        
        with sim_col1:
            st.markdown("##### ⚙️ 거래 환경 설정 (Parameters)")
            capital_krw = st.number_input(
                "투자 총 자본금 (KRW)", 
                min_value=1_000_000, 
                max_value=10_000_000_000, 
                value=50_000_000, 
                step=5_000_000,
                format="%d"
            )
            
            st.markdown("###### 거래 수수료 세부 설정")
            # 국내 거래세 및 수수료
            brokerage_kr = st.slider("국내주식 거래수수료율 (%)", 0.0, 0.5, 0.015, step=0.005, format="%.3f%%")
            tax_kr = st.slider("국내 거래세율 (%)", 0.0, 0.5, 0.18, step=0.01, format="%.2f%%")
            
            # 미국 거래 수수료
            brokerage_us = st.slider("미국주식 거래수수료율 (%)", 0.0, 0.5, 0.05, step=0.01, format="%.2f%%")
            
            # 환전 우대 및 스프레드
            fx_spread = st.slider("환전 스프레드 / 수수료율 (%)", 0.0, 1.5, 0.20, step=0.05, format="%.2f%%")
            
            # ADR custodian conversion fee
            adr_conv_fee_per_share = st.number_input(
                "ADR 취소/전환 비용 (ADR당 달러)", 
                min_value=0.0, 
                max_value=1.0, 
                value=0.05, 
                step=0.01,
                format="%.2f"
            )

        with sim_col2:
            st.markdown("##### 📊 시뮬레이션 최종 손익 (Result)")
            
            # 시나리오 1. KRX -> ADR (Premium > 0 일 때 추천)
            # -----------------------------------------------
            cost_brokerage_kr = capital_krw * (brokerage_kr / 100)
            # 국내 매수 단계 (거래세 발생 X)
            buy_power_krw = capital_krw - cost_brokerage_kr
            shares_bought = buy_power_krw / p_krx
            
            # 본주 -> ADR 전환 단계
            adrs_converted = shares_bought * adr_ratio
            adr_fee_usd = adrs_converted * adr_conv_fee_per_share
            adr_fee_krw = adr_fee_usd * fx_rate
            
            # 미국 시장 매도 단계
            adr_value_usd = adrs_converted * p_adr
            cost_brokerage_us = adr_value_usd * (brokerage_us / 100)
            net_proceeds_usd = adr_value_usd - cost_brokerage_us - adr_fee_usd
            
            # USD -> KRW 환전 (환전 스프레드 감안한 매입 환율 적용)
            fx_conversion_rate = fx_rate * (1 - fx_spread/100)
            net_proceeds_krw = net_proceeds_usd * fx_conversion_rate
            
            profit_krw_1 = net_proceeds_krw - capital_krw
            roi_1 = (profit_krw_1 / capital_krw) * 100
            
            # 시나리오 2. ADR -> KRX (Premium < 0 일 때 추천)
            # -----------------------------------------------
            # KRW -> USD 환전
            fx_buy_rate = fx_rate * (1 + fx_spread/100)
            capital_usd = capital_krw / fx_buy_rate
            
            # 미국 ADR 매수 단계
            cost_brokerage_us_2 = capital_usd * (brokerage_us / 100)
            buy_power_usd = capital_usd - cost_brokerage_us_2
            adrs_bought = buy_power_usd / p_adr
            
            # ADR -> 본주 전환 단계
            shares_converted = adrs_bought / adr_ratio
            adr_fee_usd_2 = adrs_bought * adr_conv_fee_per_share
            adr_fee_krw_2 = adr_fee_usd_2 * fx_rate
            
            # 국내 매도 단계 (거래세 + 브로커 수수료 발생)
            krx_value_krw = shares_converted * p_krx
            cost_brokerage_kr_2 = krx_value_krw * (brokerage_kr / 100)
            cost_tax_kr_2 = krx_value_krw * (tax_kr / 100)
            
            net_proceeds_krw_2 = krx_value_krw - cost_brokerage_kr_2 - cost_tax_kr_2 - adr_fee_krw_2
            
            profit_krw_2 = net_proceeds_krw_2 - capital_krw
            roi_2 = (profit_krw_2 / capital_krw) * 100
            
            # 현재 프리미엄 방향에 따른 유불리 시나리오 추천
            if premium_pct >= 0:
                trade_direction = "국내 본주 매수 ➔ 미국 ADR 전환 후 매도 (ADR 고평가 활용)"
                net_profit = profit_krw_1
                roi = roi_1
                total_fees_krw = cost_brokerage_kr + adr_fee_krw + (cost_brokerage_us * fx_rate) + (capital_krw * (fx_spread/100))
                
                steps_html = f"""
                <div style="font-size:0.82rem; line-height: 1.6;">
                    1. <b>본주 매수</b>: {capital_krw:,.0f} KRW으로 한국 시장에서 SK하이닉스 <b>{shares_bought:.2f}주</b> 매수 (수수료: {cost_brokerage_kr:,.0f} KRW)<br>
                    2. <b>ADR 교환</b>: 수탁 은행을 통해 <b>{adrs_converted:.2f} ADR</b>로 전환 취득 (ADR 수수료: ${adr_fee_usd:.2f} / {adr_fee_krw:,.0f} KRW)<br>
                    3. <b>미국 매도</b>: NASDAQ에서 주당 ${p_adr:.2f}에 매도하여 총 <b>${adr_value_usd:,.2f}</b> 취득 (수수료: ${cost_brokerage_us:.2f})<br>
                    4. <b>원화 환전</b>: 환전 스프레드 {fx_spread}% 반영 환율({fx_conversion_rate:,.2f} ₩) 적용 환전 ➔ 최종 회수액: <b>{net_proceeds_krw:,.0f} KRW</b>
                </div>
                """
            else:
                trade_direction = "미국 ADR 매수 ➔ 국내 본주 전환 후 매도 (ADR 저평가 활용)"
                net_profit = profit_krw_2
                roi = roi_2
                total_fees_krw = (cost_brokerage_us_2 * fx_rate) + adr_fee_krw_2 + cost_brokerage_kr_2 + cost_tax_kr_2 + (capital_krw * (fx_spread/100))
                
                steps_html = f"""
                <div style="font-size:0.82rem; line-height: 1.6;">
                    1. <b>달러 환전</b>: {capital_krw:,.0f} KRW을 달러로 환전 (환전 스프레드 {fx_spread}% 적용 환율 {fx_buy_rate:,.2f} ₩) ➔ <b>${capital_usd:,.2f} USD</b> 확보<br>
                    2. <b>ADR 매수</b>: 미국 NASDAQ에서 <b>{adrs_bought:.2f} ADR</b> 매수 (수수료: ${cost_brokerage_us_2:.2f})<br>
                    3. <b>본주 전환</b>: 예탁 은행에 취소 요청하여 <b>{shares_converted:.2f}주</b> 실물 본주 취득 (ADR 수수료: ${adr_fee_usd_2:.2f} / {adr_fee_krw_2:,.0f} KRW)<br>
                    4. <b>본주 매도</b>: KRX 시장에서 주당 {p_krx:,.0f} KRW에 매도 (수수료: {cost_brokerage_kr_2:,.0f} KRW, 거래세: {cost_tax_kr_2:,.0f} KRW) ➔ 최종 회수액: <b>{net_proceeds_krw_2:,.0f} KRW</b>
                </div>
                """
                
            badge_color = "badge-green" if net_profit > 0 else "badge-red"
            sim_table = (
                f'<div style="background: var(--bg-subtle); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.25rem 1.4rem; box-shadow: var(--shadow); margin-bottom:1rem;">'
                f'<div style="font-size:0.75rem; color:var(--text-muted); font-weight:600; text-transform:uppercase; letter-spacing:0.05em;">추천 거래 차익 시나리오</div>'
                f'<div style="font-size:1.15rem; font-weight:800; color:var(--text); margin-top:2px; margin-bottom: 0.8rem;">{trade_direction}</div>'
                f'<table style="width:100%; font-size:0.85rem; border-collapse: collapse;">'
                f'<tr style="border-bottom: 1px solid var(--border-subtle);"><td style="padding: 0.5rem 0; color:var(--text-muted);">총 투자금액 (Capital)</td><td style="padding: 0.5rem 0; text-align:right; font-weight:600;">{capital_krw:,.0f} KRW</td></tr>'
                f'<tr style="border-bottom: 1px solid var(--border-subtle);"><td style="padding: 0.5rem 0; color:var(--text-muted);">합산 예상 거래비용 (Total Costs)</td><td style="padding: 0.5rem 0; text-align:right; font-weight:600; color:var(--red);">{total_fees_krw:,.0f} KRW</td></tr>'
                f'<tr style="border-bottom: 1px solid var(--border-subtle);"><td style="padding: 0.5rem 0; color:var(--text-muted);">시장 가격 프리미엄 괴리율</td><td style="padding: 0.5rem 0; text-align:right; font-weight:600; color:var(--accent);">{premium_pct:+.2f}%</td></tr>'
                f'<tr style="border-bottom: 1px solid var(--border-subtle);"><td style="padding: 0.5rem 0; color:var(--text-muted);"><b>제반비용 차감 후 예상 순수익</b></td><td style="padding: 0.5rem 0; text-align:right; font-weight:700;"><span class="badge {badge_color}" style="font-size:0.85rem; padding: 3px 10px;">{net_profit:+,.0f} KRW</span></td></tr>'
                f'<tr><td style="padding: 0.5rem 0; color:var(--text-muted);">수수료 차감 후 최종 수익률 (Net ROI)</td><td style="padding: 0.5rem 0; text-align:right; font-weight:700; color: {"var(--green)" if roi > 0 else "var(--red)"};">{roi:+.3f}%</td></tr>'
                f'</table>'
                f'</div>'
            )
            st.markdown(sim_table, unsafe_allow_html=True)
            
            process_detail = (
                f'<div style="background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem 1.2rem;">'
                f'<div style="font-size:0.78rem; font-weight:600; color:var(--text); margin-bottom: 0.5rem; text-transform:uppercase;">프로세스 상세 진행 단계</div>'
                f'{steps_html}'
                f'</div>'
            )
            st.markdown(process_detail, unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # 탭 3: 차익거래 이론 및 가이드
    # --------------------------------------------------------------------------
    with tab_education:
        st.markdown("### 📘 SK하이닉스 본주 및 미국 ADR 아비트리지 거래 가이드")
        
        st.markdown("""
        #### 1. 주식 차익거래(Arbitrage)와 일물일가의 법칙
        이 대시보드는 동일 기업의 서로 다른 주식 시장 거래 자산 간의 가치가 동일하게 수렴한다는 금융 원칙에 기반합니다.
        SK하이닉스 본주(`000660`)와 미국 나스닥에 상장된 ADR(`SKHY`, 전환비율 1:10)은 본질적으로 같은 주식입니다. 
        원/달러 환율과 수수료를 감안한 실제 환산 가치가 두 시장에서 다르게 나타날 때, 상대적으로 싼 시장의 자산을 사고 비싼 시장에서 팔아 무위험 차익(Arbitrage Profit)을 내는 거래를 실행해 볼 수 있습니다.

        #### 2. 실제 아비트리지 프로세스
        차익거래를 현실화하기 위해선 주식을 반대편 시장으로 **전환 및 해지(Cancellation & Issuance)**하는 과정을 밟아야 합니다.
        
        *   **본주 ➔ ADR 전환**: 한국 거래소(KRX)에서 SK하이닉스 본주 매수 후 예탁결제원 및 주관 보관기관(Custodian Bank, 예: Citibank)을 통해 ADR로 전환(Deposit) 요청을 접수하여 미국 NASDAQ 시장에서 매도합니다.
        *   **ADR ➔ 본주 전환**: 미국 시장에서 ADR 매수 후 예탁 기관에 전환 취소(Cancellation/Withdrawal)를 신청하여 한국 예탁원으로 본주 실물을 반입한 뒤 한국 시장에서 매도합니다.

        #### 3. 차익거래 장벽 및 주요 유의사항
        실제 개인투자자 및 국내 거래 환경에선 다음과 같은 리스크를 각별히 주의해야 합니다.
        
        *   **시간 지연에 따른 주가 변동성 (Execution/Settlement Delay)**: 한국주식 매입 후 미국 ADR로 배정받는 데 보통 영업일 기준 **T+2일 이상** 소요됩니다. 거래를 개시한 시점부터 최종 청산될 때까지의 주가 하락 폭이 프리미엄 차익 폭보다 클 경우 손실이 발생할 수 있습니다.
        *   **환율 연동 리스크 (FX Risk)**: 해외 결제가 수반되는 과정 중 달러 가치가 하락(원화 강세)하면, 미국에서 회수하는 자산 가치가 훼손될 수 있습니다.
        *   **환전 및 보관 은행 수수료 (Custodian & FX Fees)**: 보관 은행(Depositary Bank)에서 청구하는 ADR 발행/해지 수수료(일반적으로 ADR당 **$0.05**) 및 은행 환전 스프레드가 지속적으로 누적됩니다.
        *   **제도적 제한 (Regulatory Issues)**: 대한민국의 외국환거래법 규정상, 단기 차익거래 목적의 개인 외환 송금이나 비거주자 간 영수 행위는 금액 및 세무 신고 요건을 충족해야 합니다.
        """)

# ==============================================================================
# 푸터 영역
# ==============================================================================
st.markdown("---")
st.markdown(
    "<div style='text-align: center; font-size: 0.72rem; color: #71717a; padding: 10px 0;'>"
    "SK Hynix Arbitrage Dashboard Pro • 한국투자증권 실시간 API 연동 버전. "
    "모든 수치는 투자 참고 지표이며 실제 환율 및 거래 세부 비용에 따라 차이가 있을 수 있습니다. 기준 시간: 2026-07-24."
    "</div>", 
    unsafe_allow_html=True
)

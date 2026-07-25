# SK Hynix Ordinary & ADR Arbitrage Tracker (with KIS API)

이 프로젝트는 SK하이닉스 본주(KRX: `000660`)와 미국 NASDAQ에 상장된 ADR(NASDAQ: `SKHY` 또는 OTC: `HXSCF`) 간의 가격 괴리율(프리미엄/할인)을 분석하고 차익거래(Arbitrage) 기회를 모니터링하기 위한 한국어 지원 Streamlit 대시보드 웹 애플리케이션입니다.

낮 시간대 한국 거래소 장중 딜레이가 없는 가격 조회를 위해 **한국투자증권 Open API**를 통한 실시간 호가 조회를 기본 지원하며, 토큰 발급 횟수 초과 및 속도 저하를 막기 위해 **전역 토큰 캐싱(Global Token Caching)** 설계를 적용했습니다. API Key가 설정되지 않았거나 조회가 실패할 경우 자동으로 `yfinance` 시세(15분 지연)로 안전하게 전환(Fallback)됩니다.

## 주요 기능 (Key Features)

1. **실시간 프리미엄 모니터링 및 한국어 UI**
   - 모든 화면 레이아웃, 지표 카드, 설명 및 차트 툴팁을 완벽한 한국어로 제공합니다.
   - SK하이닉스 본주 가격, ADR 가격, 원/달러 환율(`USDKRW=X`)을 바탕으로 실시간 프리미엄/할인율을 계산하여 표시합니다.

2. **한국투자증권 Open API 연동 (낮 시간 실시간 주가)**
   - 국내 장중 정규 거래 시간대(`09:00 ~ 15:30`) 동안 딜레이 없는 실시간 주가를 제공합니다.
   - **글로벌 토큰 공유 캐시**(`@st.cache_data(ttl=86000)`): 웹 사이트에 방문하는 모든 사용자가 하나의 Access Token을 공유하여 불필요한 토큰 발행 및 API 제한 한도를 완벽히 회피합니다.

3. **거래소 운영 시간대 트래커 (Timezone-Aware Tracker)**
   - 한국 시간(KST) 및 미국 동부 시간(EST/EDT)을 기준으로 두 거래소의 실시간 상태(정규장, 프리마켓, 애프터마켓, 휴장 등)를 한눈에 확인할 수 있습니다.

4. **과거 추이 차트 및 통계 데이터**
   - Plotly 기반의 과거 프리미엄 변동 그래프와 3대 지표 정규화(Base 100) 비교 차트 제공.
   - 평균 프리미엄, 프리미엄 변동성(표준편차), 최대 할증/최대 할인을 제공합니다.

5. **아비트리지 실거래 시뮬레이터 (Arbitrage Simulator)**
   - '본주 매수 후 미국 ADR 전환 매도' 또는 'ADR 매수 후 본주 전환 매도' 프로세스별 발생 비용(국내외 주식 수수료, 환전 스프레드, 국내 거래세, ADR 수탁 수수료 등)을 차감하여 세후 ROI와 예상 순수익을 시뮬레이션합니다.

---

## 실행 방법 (How to Run Locally)

### 1. 패키지 설치
Python 3.8 이상 환경에서 다음 명령어를 실행하여 필수 라이브러리를 설치합니다.
```bash
# 가상환경 생성 및 활성화
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# 또는 .venv\Scripts\activate  # Windows

# 의존성 패키지 설치
pip install -r requirements.txt
```

### 2. API Key 설정 (선택 사항)
* 대시보드 화면 내 사이드바의 **"한국투자증권 OpenAPI 연동 설정"** 영역에 직접 `App Key` 및 `App Secret`을 입력하여 로컬 세션에 반영할 수 있습니다.
* 또는 로컬 프로젝트 내 `.streamlit/secrets.toml` 파일을 생성하여 다음과 같이 등록해 두시면 자동으로 불러옵니다.
  ```toml
  KIS_APP_KEY = "발급받은_App_Key"
  KIS_APP_SECRET = "발급받은_App_Secret"
  ```

### 3. 애플리케이션 실행
```bash
streamlit run streamlit_app.py
```
브라우저에서 `http://localhost:8501`로 대시보드에 접속합니다.

---

## 깃허브 배포 및 Streamlit Cloud 호스팅 방법

실제 라이브 웹 사이트로 배포하여 고유 주소(`https://hynix-arbit.streamlit.app`)로 접속하려면 아래 과정을 따릅니다.

### 1. GitHub 리포지토리로 푸시
1. GitHub 웹사이트에서 새로운 빈 리포지토리(예: `hynix-adr-arbitrage`)를 생성합니다.
2. 로컬 터미널에서 깃 원격 저장소를 지정하고 푸시합니다.
   ```bash
   git remote add origin https://github.com/당신의유저네임/리포지토리이름.git
   git branch -M main
   git push -u origin main
   ```

### 2. Streamlit Community Cloud 배포 및 도메인 설정
1. [Streamlit Share](https://share.streamlit.io/)에 로그인합니다.
2. **"Create app"** 버튼을 누릅니다.
3. 자신의 깃허브 리포지토리를 선택하고, 브랜치를 `main`, 메인 파일 경로를 `streamlit_app.py`로 설정합니다.
4. **Custom URL** 설정에서 원하는 도메인명(예: `hynix-arbit`)을 기입합니다. 
   - 도메인 주소는 `https://hynix-arbit.streamlit.app` 형식이 됩니다. (서브도메인 이름 규칙상 언더스코어 `_` 대신 대시 `-` 문자가 널리 쓰입니다.)
5. **Secrets 설정 (KIS API 자동 연동)**:
   - 배포 설정 페이지의 **Advanced settings...** ➔ **Secrets** 탭으로 들어갑니다.
   - 아래 서식을 붙여넣고 저장합니다.
     ```toml
     KIS_APP_KEY = "당신의_한국투자증권_실전투자_AppKey"
     KIS_APP_SECRET = "당신의_한국투자증권_실전투자_AppSecret"
     ```
6. **"Deploy!"** 버튼을 클릭하면 배포가 시작되며, 약 1~2분 뒤 나만의 실시간 차익거래 사이트가 완성됩니다.

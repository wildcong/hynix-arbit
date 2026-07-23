# SK Hynix Ordinary & ADR Arbitrage Tracker

이 프로젝트는 SK하이닉스 본주(KRX: `000660.KS`)와 미국 NASDAQ에 상장된 ADR(NASDAQ: `SKHY` 또는 OTC: `HXSCF`) 간의 가격 괴리율(프리미엄/할인)을 실시간으로 분석하고 차익거래(Arbitrage) 기회를 모니터링하기 위한 Streamlit 대시보드 웹 애플리케이션입니다.

"일물일가(Law of One Price)" 이론을 현실적인 거래 수수료, 환전 스프레드 및 보관 수수료 등 거래 비용 모델과 결합하여 세후 순수익을 모델링하는 인터랙티브 시뮬레이터를 포함하고 있습니다.

## 주요 기능 (Key Features)

1. **실시간 프리미엄 모니터링 (Real-time Premium Tracking)**
   - SK하이닉스 본주 가격, ADR 가격, 원/달러 환율(`USDKRW=X`)을 바탕으로 실시간 프리미엄/할인율 계산.
   - 본주 대비 ADR의 일물일가 적정 가치(Implied Value)를 산출하여 괴리 상태(할증/할인/적정) 표시.

2. **시장 시간대 트래커 (Zone-Aware Market Hours)**
   - 한국 시간(KST) 및 미국 동부 시간(EST/EDT)을 기준으로 두 시장의 실시간 운영 상태(정규장, 프리마켓, 애프터마켓, 휴장 등) 시각화.

3. **가격 변동성 및 과거 프리미엄 추이 차트 (Historical Volatility)**
   - Plotly 기반의 과거 프리미엄 괴리율 변동성 차트 및 정규화(Base 100) 가격 비교 차트 제공.
   - 조회 기간 설정 기능(5일, 1개월, 3개월, 6개월, 1년).

4. **아비트리지 실거래 시뮬레이터 (Arbitrage Simulator)**
   - 설정 투자금에 따라 '국내 본주 매수 후 미국 ADR 매도' 또는 '미국 ADR 매수 후 국내 본주 매도' 시나리오에 따른 수수료 차감 후 예상 순수익 및 투자수익률(ROI) 계산.
   - 국내외 브로커리지 수수료, 국내 거래세, 환전 스프레드, ADR 전환 비용($0.05/ADR)을 모두 커스터마이징 가능.

5. **이론 및 위험 가이드 (Educational Guide)**
   - 차익거래의 금융 이론적 배경과 실행 절차, 그리고 현실적인 법적 규제(외국환거래법), 시간차 리스크, 대차 비용 등에 대한 가이드 제공.

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

### 2. 애플리케이션 실행
가상환경이 활성화된 상태에서 Streamlit 서버를 실행합니다.
```bash
streamlit run streamlit_app.py
```
실행 후 브라우저에서 `http://localhost:8501`로 대시보드에 접속할 수 있습니다.

---

## 깃허브 배포 방법 (How to Deploy / Push to GitHub)

본 로컬 저장소를 자신의 GitHub 리포지토리에 푸시하려면 아래 절차를 진행해 주세요.

1. **GitHub 리포지토리 생성**: GitHub 사이트에서 새로운 빈 리포지토리(예: `hynix-adr-arbitrage`)를 생성합니다.
2. **로컬 Git 초기화 및 커밋**:
   ```bash
   git init
   git add .
   git commit -m "feat: SK Hynix ADR arbitrage dashboard initial commit"
   ```
3. **원격 저장소 추가 및 푸시**:
   ```bash
   git branch -M main
   git remote add origin https://github.com/사용자이름/리포지토리이름.git
   git push -u origin main
   ```
4. **Streamlit Community Cloud 배포 (선택 사항)**:
   - [Streamlit Share](https://share.streamlit.io/)에 가입하고 생성한 깃허브 저장소를 연동하면, 단 몇 번의 클릭으로 무료 웹 URL로 즉시 배포하여 모바일이나 다른 기기에서도 대시보드를 보실 수 있습니다.

# Simple Finance Trading Bot

바이낸스 선물 데이터를 수집하고 트레이딩 신호를 생성하는 자동화 시스템

## 🚀 빠른 시작

### 가상환경 설정
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt
```

### Docker 설정
```bash
# Docker 이미지 빌드
docker build -t simple-finance .

# 컨테이너 실행
docker run -it --rm simple-finance

# 이미지 내보내기 (다른 컴퓨터로 이동용)
docker save -o simple-finance.tar simple-finance

# 이미지 불러오기 (다른 컴퓨터에서)
docker load -i simple-finance.tar
```

## 📁 모듈 구조

### 핵심 모듈
- **`main.py`** - 메뉴 기반 사용자 인터페이스
- **`client.py`** - CCXT를 통한 바이낸스 API 연결 및 데이터 수집
- **`db.py`** - SQLite 데이터베이스 관리 (종목별 OHLCV 데이터 저장)
- **`config.py`** - 설정 파일 (시작 시간, 기본 간격 등)

### 트레이딩 모듈 (개발 예정)
- **`model.py`** - 트레이딩 모델 (Transformer, 강화학습)
- **`signgen.py`** - 매수/매도 신호 생성 로직
- **`train.py`** - 모델 훈련 및 최적화
- **`backtest.py`** - 백테스팅 시스템

## 🔧 작동 방식

1. **데이터 수집**: 바이낸스 선물에서 1분 간격 OHLCV 데이터 수집
2. **데이터 저장**: 종목별로 SQLite 테이블에 저장
3. **신호 생성**: 기술적 지표 기반 매수/매도 신호 생성
4. **백테스팅**: 과거 데이터로 전략 성능 검증
5. **실시간 모니터링**: 현재 시장 상황 분석

## 📅 개발 일정

### ✅ 완료 (2025-07-03)
- [x] 바이낸스 API 연동 (CCXT)
- [x] SQLite 데이터베이스 구조 설계
- [x] 종목별 OHLCV 데이터 수집 및 저장
- [x] 메뉴 기반 사용자 인터페이스
- [x] Docker 컨테이너화
- [x] 에러 처리 및 성능 최적화

### 🔄 진행 예정

#### Phase 1: 기본 트레이딩 모델 (1주)
- [ ] 기술적 지표 구현 (이동평균, RSI, MACD)
- [ ] 기본 매수/매도 신호 생성
- [ ] 단순 백테스팅 시스템

#### Phase 2: Transformer 모델 (2주)
- [ ] Transformer 기반 시계열 예측 모델 구현
- [ ] Attention 메커니즘을 활용한 가격 패턴 학습
- [ ] 모델 훈련 및 하이퍼파라미터 최적화

#### Phase 3: 강화학습 시스템 (2주)
- [ ] 강화학습 환경 구축 (환경, 에이전트, 보상 함수)
- [ ] DQN, A2C 등 강화학습 알고리즘 구현
- [ ] 실시간 신호 생성 및 백테스팅

#### Phase 4: 성능 최적화 (1주)
- [ ] 모델 성능 최적화
- [ ] 성능 지표 계산 (Sharpe Ratio, Max Drawdown)
- [ ] 실시간 알림 시스템 (텔레그램)

## 📊 데이터베이스 구조

```
symbols 테이블:
- id (PK)
- symbol (종목명)
- interval (시간간격)
- last_timestamp (최신 데이터 시간)

ohlcv_{symbol} 테이블 (종목별):
- id (PK)
- timestamp (시간)
- open, high, low, close, volume (OHLCV)
```

## ⚙️ 설정

`config.py`에서 다음 설정을 변경할 수 있습니다:
- `DATA_START_TIMESTAMP`: 데이터 수집 시작 시간
- `DEFAULT_INTERVAL`: 기본 시간 간격
- `DB_PATH`: 데이터베이스 파일 경로 
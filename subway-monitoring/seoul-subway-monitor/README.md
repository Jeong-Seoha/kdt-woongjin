# Seoul Subway Real-time Monitoring System

서울시 지하철 실시간 위치 정보를 수집하여 데이터베이스에 적재하고, 운행 정시성 및 지연 등을 분석하는 시스템입니다.

## 1. 사전 준비 (Setup)

### 필수 요구사항
- Python 3.10+
- Supabase 계정 및 Project

### 설치
```bash
pip install -r requirements.txt
```

### 환경 설정 (.env)
다음 변수들이 `.env` 파일에 설정되어 있어야 합니다.
- `SEOUL_API_KEY`: 서울시 열린데이터 광장 API Key
- `SUPABASE_URL`: Supabase Project URL
- `SUPABASE_KEY`: Supabase Service Role Key (또는 Anon Key + RLS 설정)

## 2. 데이터베이스 구축 (Supabase)
API 키만으로는 테이블을 생성할 수 없으므로, **Supabase Dashboard > SQL Editor**에서 다음 파일들의 내용을 순서대로 실행해주세요.

1. **테이블 생성**: [`docs/schema.sql`](docs/schema.sql)
   - `realtime_subway_positions` 테이블을 생성합니다.
   
2. **분석 뷰 생성**: [`docs/analysis_queries.sql`](docs/analysis_queries.sql)
   - 데이터 분석을 위한 4가지 SQL View를 생성합니다. (배차간격, 지연구간, 회차효율, 혼잡도)

## 3. 실행 방법 (Usage)

### 데이터 수집 에이전트 실행
1분 간격으로 데이터를 수집하여 DB에 저장합니다.
```bash
python3 -m src.main
```

### 실행 확인
- 터미널에 "75건의 데이터가 성공적으로 저장되었습니다." 등의 로그가 출력되면 정상 동작 중인 것입니다.
- Supabase Dashboard의 Table Editor에서 데이터가 쌓이는 것을 확인할 수 있습니다.

## 4. 데이터 분석
데이터가 충분히(약 1시간 이상) 쌓인 후, Supabase Dashboard에서 다음 View들을 조회하여 인사이트를 얻을 수 있습니다.

- `view_interval_regularity`: 배차 간격 확인
- `view_dwell_time`: 역별 정차 시간 확인
- `view_turnaround_monitoring`: 회차 모니터링
- `view_express_local_congestion`: 급행/일반 간섭 확인

또는 다음 파이썬 스크립트를 실행하여 터미널에서 분석 리포트를 즉시 확인할 수 있습니다:
```bash
python3 -m src.analysis_runner
```


-- 데이터 분석을 위한 SQL 쿼리 및 View 정의
-- docs/analysis_plan.md 에 정의된 4가지 분석 목표를 구현합니다.

-- 1. 배차 간격 정기성 분석 (Interval Regularity)
-- 특정 역, 호선, 방향별로 열차 도착 시간 차이(Headway) 계산
CREATE OR REPLACE VIEW view_interval_regularity AS
WITH arrival_data AS (
    SELECT 
        line_id,
        station_name,
        direction_type,
        train_number,
        created_at,
        LAG(created_at) OVER (PARTITION BY line_id, station_name, direction_type ORDER BY created_at) as prev_arrival_time
    FROM realtime_subway_positions
    WHERE train_status = '1' -- 도착 상태인 경우만
)
SELECT 
    *,
    EXTRACT(EPOCH FROM (created_at - prev_arrival_time)) as interval_seconds
FROM arrival_data
WHERE prev_arrival_time IS NOT NULL;


-- 2. 지연 발생구간 탐지 (Delay Hotspots)
-- 역별 체류 시간 (도착(1) -> 출발(2) 소요 시간)
-- 같은 날짜, 같은 열차, 같은 역세서 발생한 도착과 출발 이벤트의 시간차
CREATE OR REPLACE VIEW view_dwell_time AS
WITH arrivals AS (
    SELECT train_number, station_name, created_at as arrive_time
    FROM realtime_subway_positions
    WHERE train_status = '1'
),
departures AS (
    SELECT train_number, station_name, created_at as depart_time
    FROM realtime_subway_positions
    WHERE train_status = '2'
)
SELECT 
    a.train_number,
    a.station_name,
    a.arrive_time,
    d.depart_time,
    EXTRACT(EPOCH FROM (d.depart_time - a.arrive_time)) as dwell_seconds
FROM arrivals a
JOIN departures d ON a.train_number = d.train_number AND a.station_name = d.station_name
WHERE d.depart_time > a.arrive_time
  AND d.depart_time < a.arrive_time + interval '1 hour'; -- 1시간 이내 매칭 (오류 방지)


-- 3. 회차 효율성 분석 (Turnaround Efficiency)
-- 종착역 도착 후 반대 방향으로 변경되는 시간
-- 로직: 종착역명이 현재 역명과 같고, 이후 방향이 바뀌는 케이스 (복잡하므로 근사치 쿼리)
-- 여기서는 단순히 종착역에 있는 열차들의 상태를 모니터링
CREATE OR REPLACE VIEW view_turnaround_monitoring AS
SELECT 
    line_id,
    train_number,
    station_name,
    direction_type,
    created_at
FROM realtime_subway_positions
WHERE station_name = dest_station_name;


-- 4. 급행/일반 열차 간섭 분석
-- 급행(1)과 일반(0) 열차의 위치 목록 
CREATE OR REPLACE VIEW view_express_local_congestion AS
SELECT 
    line_id,
    direction_type,
    station_name,
    is_express,
    train_number,
    train_status,
    created_at
FROM realtime_subway_positions
ORDER BY line_id, direction_type, created_at DESC;

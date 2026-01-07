import time
import schedule
from src.config import Config
from src.api_client import SeoulSubwayClient
from src.db_client import SupabaseClient

def job():
    """
    주기적으로 실행될 작업: 데이터 수집 -> DB 저장
    """
    print(f"[Job Start] {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 설정 검증
    try:
        Config.validate()
    except ValueError as e:
        print(f"설정 오류: {e}")
        return

    api_client = SeoulSubwayClient()
    db_client = SupabaseClient()
    
    # 수집할 호선 목록 (필요 시 확장)
    target_lines = ["1호선"] 
    
    for line in target_lines:
        print(f"'{line}' 데이터 수집 중...")
        positions = api_client.get_realtime_positions(line_name=line)
        
        if positions:
            print(f"'{line}' - {len(positions)}개의 열차 정보 수신. DB 저장 시도.")
            db_client.insert_positions(positions)
        else:
            print(f"'{line}' - 수신된 데이터 없음.")
            
    print(f"[Job End] {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

def main():
    print("서울 지하철 실시간 모니터링 시스템을 시작합니다.")
    
    # 최초 1회 즉시 실행
    job()
    
    # 주기 설정 (예: 60초마다 실행)
    schedule.every(60).seconds.do(job)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n시스템을 종료합니다.")

if __name__ == "__main__":
    main()

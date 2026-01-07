from src.db_client import SupabaseClient
import datetime
from collections import defaultdict

class AnalysisRunner:
    """
    Supabase Views or Raw Data를 사용하여 분석 리포트를 생성하는 클래스
    Views가 없으면 파이썬에서 직접 계산하여 결과를 보여줍니다.
    """
    
    def __init__(self):
        self.db_client = SupabaseClient()
        self.raw_data_cache = None
        
    def fetch_raw_data(self, limit=1000):
        """최신 로우 데이터 캐싱"""
        if self.raw_data_cache is None:
            try:
                # Fetch recent data for python-side analysis
                res = self.db_client.client.table("realtime_subway_positions")\
                    .select("*").order("created_at", desc=True).limit(limit).execute()
                self.raw_data_cache = res.data
                print(f"[Info] 로우 데이터 {len(self.raw_data_cache)}건 로드 완료 (Python 분석용)")
            except Exception as e:
                print(f"[Warn] 데이터 로드 실패: {e}")
                self.raw_data_cache = []
        return self.raw_data_cache

    def run_all(self):
        print(f"=== [분석 시작] {datetime.datetime.now()} ===")
        self.check_interval_regularity()
        self.check_delay_hotspots()
        self.check_turnaround_efficiency()
        self.check_express_congestion()
        print("=== [분석 종료] ===")

    def check_interval_regularity(self):
        print("\n1) 배차 간격 정기성 분석 (Interval Regularity)")
        try:
            response = self.db_client.client.table("view_interval_regularity").select("*").limit(10).execute()
            data = response.data
            if not data: print("- View 데이터 없음")
            for row in data:
                print(f" - [View] {row['line_id']} {row['station_name']} ({row['train_number']}): {row['interval_seconds']}초")
        except Exception:
            # Fallback to Python
            print("- View 조회 실패. Python으로 직접 분석합니다.")
            self.analyze_interval_py()

    def print_table(self, title, headers, rows):
        """
        간단한 ASCII 테이블 출력 헬퍼
        """
        print(f"\n[{title}]")
        if not rows:
            print("  (데이터 없음)")
            return

        # Calculate column widths
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, val in enumerate(row):
                # Count length properly for Korean characters?
                # Simple len() might be short for Korean, but let's stick to basic padding first.
                # For better alignment with Korean, we usually need specific handling, 
                # but standard ljust/rjust with some buffer is a good start.
                s_val = str(val)
                # Crude estimation: Korean chars are usually width 2 in terminals
                w = 0
                for char in s_val:
                    w += 2 if ord(char) > 500 else 1
                if w > col_widths[i]:
                    col_widths[i] = w

        # Create format string
        # To align nicely, we might need a custom printer. 
        # Let's try simple tab-separated or fixed width with visual check.
        
        # Build header
        header_line = " | ".join([h.ljust(col_widths[i] - (len(h.encode()) - len(h)) // 2) for i, h in enumerate(headers)])
        separator = "-+-".join(["-" * w for w in col_widths])
        
        print(header_line)
        print(separator)
        
        for row in rows:
            line_parts = []
            for i, val in enumerate(row):
                s_val = str(val)
                # Pad based on visual length
                visual_len = 0
                for char in s_val:
                    visual_len += 2 if ord(char) > 127 else 1
                
                pad = col_widths[i] - visual_len
                line_parts.append(s_val + " " * pad)
            print(" | ".join(line_parts))

    def analyze_interval_py(self):
        data = self.fetch_raw_data(limit=1500)
        train_arrivals = {}
        for row in data:
            if row['train_status'] == '1':
                key = (row['line_id'], row['station_name'], row['direction_type'], row['train_number'])
                ts = datetime.datetime.fromisoformat(row['created_at'].replace('Z', '+00:00'))
                if key not in train_arrivals or ts < train_arrivals[key]:
                    train_arrivals[key] = ts
        
        station_groups = defaultdict(list)
        for (line, station, direction, train_num), time in train_arrivals.items():
            station_groups[(line, station, direction)].append((train_num, time))
            
        rows = []
        count = 0
        sorted_groups = sorted(station_groups.items(), key=lambda x: len(x[1]), reverse=True)
        
        for (line, station, direction), arrivals in sorted_groups:
            if len(arrivals) < 2: continue
            arrivals.sort(key=lambda x: x[1])
            for i in range(len(arrivals) - 1):
                train_a, time_a = arrivals[i]
                train_b, time_b = arrivals[i+1]
                diff = (time_b - time_a).total_seconds()
                if diff > 30:
                    dir_str = "상행" if direction == "0" else "하행"
                    rows.append([line, station, dir_str, f"{train_a} -> {train_b}", f"{diff/60:.1f}분"])
                    count += 1
            if count >= 10: break
            
        self.print_table("1) 배차 간격 정기성 TOP 10", ["호선", "역명", "방향", "열차행렬", "간격"], rows)

    def check_delay_hotspots(self):
        print("\n2) 지연 발생구간 탐지 (Delay Hotspots)")
        try:
            response = self.db_client.client.table("view_dwell_time").select("*").limit(10).execute()
            rows = [[r['station_name'], r['train_number'], f"{r['dwell_seconds']}초"] for r in response.data]
            self.print_table("2) 지연 발생(체류시간) TOP 10 (View)", ["역명", "열차번호", "체류시간"], rows)
        except Exception:
            print("- View 조회 실패. Python으로 직접 분석합니다.")
            self.analyze_dwell_time_py()

    def analyze_dwell_time_py(self):
        data = self.fetch_raw_data(limit=1500)
        arrivals = {} 
        events = []
        sorted_data = sorted(data, key=lambda x: x['created_at'])
        
        for row in sorted_data:
            key = (row['train_number'], row['station_name'])
            ts = datetime.datetime.fromisoformat(row['created_at'].replace('Z', '+00:00'))
            if row['train_status'] == '1':
                if key not in arrivals: arrivals[key] = ts
            elif row['train_status'] == '2':
                if key in arrivals:
                    dwell = (ts - arrivals[key]).total_seconds()
                    if 0 < dwell < 3600:
                        events.append((row['line_id'], row['station_name'], row['train_number'], dwell))
                    del arrivals[key]
        
        events.sort(key=lambda x: x[3], reverse=True)
        rows = [[e[0], e[1], e[2], f"{e[3]:.1f}초"] for e in events[:10]]
        self.print_table("2) 지연 발생(체류시간) TOP 10", ["호선", "역명", "열차번호", "체류시간"], rows)

    def check_turnaround_efficiency(self):
        print("\n3) 회차 효율성 분석 (Turnaround Efficiency)")
        try:
            response = self.db_client.client.table("view_turnaround_monitoring").select("*").limit(10).execute()
            rows = [[r['station_name'], r['train_number']] for r in response.data]
            self.print_table("3) 회차 대기 (View)", ["역명", "열차번호"], rows)
        except Exception:
            print("- View 조회 실패. Python으로 직접 분석합니다.")
            self.analyze_turnaround_py()

    def analyze_turnaround_py(self):
        data = self.fetch_raw_data(limit=1500)
        at_dest = {}
        latest_seen = {}
        for row in data:
            if row['station_name'] == row['dest_station_name']:
                key = (row['train_number'], row['station_name'])
                ts = datetime.datetime.fromisoformat(row['created_at'].replace('Z', '+00:00'))
                if key not in at_dest or ts < at_dest[key]: at_dest[key] = ts
                if key not in latest_seen or ts > latest_seen[key]: latest_seen[key] = ts
                    
        items = []
        for key, start_ts in at_dest.items():
            duration = (latest_seen[key] - start_ts).total_seconds()
            items.append((key[0], key[1], duration))
        items.sort(key=lambda x: x[2], reverse=True)
        
        rows = [[item[1], item[0], f"{item[2]:.0f}초"] for item in items[:10]]
        self.print_table("3) 종착역 회차 대기 TOP 10", ["역명", "열차번호", "대기시간"], rows)

    def check_express_congestion(self):
        print("\n4) 급행/일반 열차 간섭 분석 (Congestion/Overtake)")
        try:
            response = self.db_client.client.table("view_express_local_congestion").select("*").limit(10).execute()
            rows = []
            for r in response.data:
                is_exp = "급행" if r['is_express'] == '1' else "일반"
                rows.append([is_exp, r['train_number'], r['station_name']])
            self.print_table("4) 급행/일반 혼잡 (View)", ["구분", "열차번호", "위치"], rows)
        except Exception:
            print("- View 조회 실패. Python으로 직접 분석합니다.")
            self.analyze_congestion_py()

    def analyze_congestion_py(self):
        data = self.fetch_raw_data(limit=1000)
        latest = {}
        for row in data:
            if row['train_number'] not in latest: latest[row['train_number']] = row
        
        express = [r for r in latest.values() if r['is_express'] == '1']
        express.sort(key=lambda x: x['created_at'], reverse=True)
        
        rows = []
        for r in express[:10]:
            st_map = {'0':'진입', '1':'도착', '2':'출발'}
            status = st_map.get(r['train_status'], r['train_status'])
            rows.append([r['train_number'], r['dest_station_name'], r['station_name'], status, "급행"])
            
        self.print_table("4) 급행 열차 운행 현황 (최근)", ["열차번호", "행선지", "현재위치", "상태", "구분"], rows)


if __name__ == "__main__":
    runner = AnalysisRunner()
    runner.run_all()

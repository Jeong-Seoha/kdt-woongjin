from supabase import create_client, Client
from src.config import Config
import datetime

class SupabaseClient:
    """
    Supabase 데이터베이스 연동 클라이언트
    """
    
    def __init__(self):
        self.url = Config.SUPABASE_URL
        self.key = Config.SUPABASE_KEY
        self.client: Client = create_client(self.url, self.key)
        self.table_name = "realtime_subway_positions"

    def insert_positions(self, positions: list):
        """
        API에서 조회한 열차 위치 정보를 DB 스키마에 맞춰 변환 후 저장합니다.
        
        Args:
            positions (list): API 원본 데이터 리스트
            
        Returns:
            list: 삽입된 데이터 리스트 또는 에러 정보
        """
        if not positions:
            return []
            
        formatted_data = []
        
        for pos in positions:
            # lstcarAt 변환 (0:아님, 1:막차 -> Boolean)
            is_last = False
            if str(pos.get("lstcarAt")) == "1":
                is_last = True
                
            record = {
                "line_id": pos.get("subwayId"),
                "line_name": pos.get("subwayNm"),
                "station_id": pos.get("statnId"),
                "station_name": pos.get("statnNm"),
                "train_number": pos.get("trainNo"),
                "last_rec_date": pos.get("lastRecptnDt"),
                "last_rec_time": pos.get("recptnDt"),
                "direction_type": pos.get("updnLine"),
                "dest_station_id": pos.get("statnTid"),
                "dest_station_name": pos.get("statnTnm"),
                "train_status": pos.get("trainSttus"),
                "is_express": pos.get("directAt"),
                "is_last_train": is_last,
                # created_at은 DB Default 값 사용 (또는 여기서 현재 시간 명시 가능)
            }
            formatted_data.append(record)
            
        try:
            # 데이터 삽입 (bulk insert)
            response = self.client.table(self.table_name).insert(formatted_data).execute()
            print(f"{len(formatted_data)}건의 데이터가 성공적으로 저장되었습니다.")
            return response.data
        except Exception as e:
            print(f"DB 저장 중 에러 발생: {e}")
            return []

import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    """
    환경 설정 관리 클래스
    """
    SEOUL_API_KEY = os.getenv("SEOUL_API_KEY")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # 서울시 실시간 지하철 위치 API URL (기본 URL)
    # 실제 호출 시에는 /{KEY}/json/realtimePosition/0/5/{호선명} 형태로 조립 필요
    BASE_API_URL = "http://swopenAPI.seoul.go.kr/api/subway"

    @staticmethod
    def validate():
        if not Config.SEOUL_API_KEY:
            raise ValueError("SEOUL_API_KEY가 설정되지 않았습니다.")
        if not Config.SUPABASE_URL:
            raise ValueError("SUPABASE_URL이 설정되지 않았습니다.")
        if not Config.SUPABASE_KEY:
            raise ValueError("SUPABASE_KEY가 설정되지 않았습니다.")

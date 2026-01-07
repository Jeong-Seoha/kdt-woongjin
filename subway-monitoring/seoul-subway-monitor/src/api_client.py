import requests
import json
from src.config import Config

class SeoulSubwayClient:
    """
    서울시 지하철 실시간 위치 API 클라이언트
    """
    
    def __init__(self):
        self.api_key = Config.SEOUL_API_KEY
        self.base_url = Config.BASE_API_URL

    def get_realtime_positions(self, line_name: str):
        """
        특정 호선의 실시간 열차 위치 정보를 조회합니다.
        
        Args:
            line_name (str): 조회할 호선명 (예: "1호선", "2호선")
            
        Returns:
            list: 열차 위치 정보 리스트 (API 응답의 'realtimePositionList')
            
        Raises:
            Exception: API 호출 실패 시
        """
        # URL 구성: http://swopenAPI.seoul.go.kr/api/subway/{KEY}/json/realtimePosition/0/100/{line_name}
        # 한 번에 최대 100개까지 조회 (충분한 수)
        
        url = f"{self.base_url}/{self.api_key}/json/realtimePosition/0/100/{line_name}"
        
        try:
            response = requests.get(url)
            response.raise_for_status() # HTTP 에러 발생 시 예외 송출
            
            data = response.json()
            
            if 'realtimePositionList' in data:
                return data['realtimePositionList']
            else:
                # 데이터가 없거나 에러 메시지가 있는 경우
                if 'RESULT' in data and 'MESSAGE' in data['RESULT']:
                    print(f"API 호출 결과: {data['RESULT']['MESSAGE']}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"API 요청 중 에러 발생: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 에러: {e}")
            return []

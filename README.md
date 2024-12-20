# 서울 지하철 승하차 인원 조회 대시보드

## 프로젝트 소개
이 Streamlit 애플리케이션은 서울시 Open API를 활용하여 지하철 승하차 인원 데이터를 시각화하고 분석하는 도구입니다. 사용자는 특정 지하철역의 승하차 데이터를 쉽게 조회하고 분석할 수 있습니다.

## 주요 기능
- 특정 지하철역의 승하차 인원 조회
- 날짜 범위 선택 기능
- 전체 및 호선별 승하차 인원 트렌드 시각화
- 승차/하차 인원 통계 제공
- 전주, 전월, 전년 대비 증감률 계산 (선택적)
- CSV 데이터 다운로드 기능

## 요구 사항
- Python 3.7+
- Streamlit
- Pandas
- Requests

## 설치 방법
1. 저장소 클론
```bash
git clone https://github.com/adalgu/seoul-metro-openapi.git
cd seoul-metro-openapi
```

2. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

## 사용 방법
1. 서울시 Open API 인증키 준비 (https://data.seoul.go.kr/ 에서 발급)
2. 애플리케이션 실행
```bash
streamlit run app.py
```

3. 웹 인터페이스에서:
- Open API 인증키 입력
- 조회할 지하철역명 입력
- 날짜 범위 선택
- (선택) 증감률 계산 체크

## 데이터 소스
- 서울시 지하철 승하차 데이터 Open API

## 라이선스
MIT 라이선스

## 기여
이슈 및 풀 리퀘스트는 언제나 환영합니다.
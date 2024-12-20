# 서울 지하철 승하차 인원 조회 대시보드

## 프로젝트 소개
이 Streamlit 애플리케이션은 서울시 Open API를 활용하여 지하철 승하차 인원 데이터를 시각화하고 분석하는 도구입니다.

## 배포 전략

### 권장 배포 방법

#### 1. Docker 배포 (가장 추천)
```bash
# 이미지 빌드
docker build -t seoul-metro-dashboard .

# 컨테이너 실행
docker run -p 8502:8502 seoul-metro-dashboard
```

#### 2. 로컬 개발 서버
```bash
# 종속성 설치
pip install -r requirements.txt

# Streamlit 실행
streamlit run app.py
```

### 클라우드 배포 고려사항

#### Vercel 배포 제한
- Streamlit은 서버리스 환경에 최적화되지 않음
- 대용량 종속성으로 인한 배포 제한

#### 대안적 클라우드 배포 옵션
1. Heroku
2. Google Cloud Run
3. AWS Elastic Beanstalk

### 권장 배포 워크플로우
1. Docker 컨테이너화
2. 클라우드 컨테이너 서비스 활용
3. 전용 가상 머신에 직접 배포

## 주요 기능
- 지하철역 승하차 인원 조회
- 날짜 범위 선택
- 승하차 인원 트렌드 시각화
- CSV 데이터 다운로드

## 요구 사항
- Python 3.9+
- Streamlit
- Pandas
- Requests

## 라이선스
MIT 라이선스

## 기여
이슈 및 풀 리퀘스트 환영합니다.
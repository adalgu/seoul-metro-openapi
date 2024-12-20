import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import io
import calendar

# 페이지 설정
st.set_page_config(page_title="서울 지하철 승하차 인원 조회", layout="wide")
st.title("서울 지하철 승하차 인원 조회")

# API 키 입력
api_key = st.text_input("서울시 OpenAPI 인증키를 입력하세요", type="password")

# 날짜 기간 선택
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input(
        "시작일을 선택하세요",
        value=datetime.now() - timedelta(days=30)
    )
with col2:
    end_date = st.date_input(
        "종료일을 선택하세요",
        value=datetime.now() - timedelta(days=1)
    )

# 역명 입력
station_name = st.text_input("지하철역명을 입력하세요 (예: 강남, 용산, 신림, 김포공항)")

def fetch_data(date, station):
    """특정 날짜의 지하철 승하차 데이터를 가져옵니다."""
    date_str = date.strftime("%Y%m%d")
    url = f"http://openapi.seoul.go.kr:8088/{api_key}/json/CardSubwayStatsNew/1/1000/{date_str}/%20/{station}"
    
    try:
        response = requests.get(url)
        data = response.json()
        if "CardSubwayStatsNew" in data:
            # 정확한 역명 매칭을 위한 필터링
            filtered_rows = [
                row for row in data["CardSubwayStatsNew"]["row"]
                if row["SBWY_STNS_NM"] == station
            ]
            return filtered_rows
    except Exception as e:
        st.error(f"데이터 조회 중 오류 발생: {str(e)}")
    return []

def get_same_weekday_date(current_date, days_ago):
    """주어진 날짜의 n일 전 같은 요일의 날짜를 반환합니다."""
    target_date = current_date - timedelta(days=days_ago)
    while target_date.weekday() != current_date.weekday():
        target_date -= timedelta(days=1)
    return target_date

def calculate_change_rates(df, current_date):
    """기간대비 증감률을 계산합니다."""
    daily_total = df.groupby('USE_YMD').agg({
        'GTON_TNOPE': 'sum',
        'GTOFF_TNOPE': 'sum'
    }).reset_index()
    daily_total['total'] = daily_total['GTON_TNOPE'] + daily_total['GTOFF_TNOPE']
    
    current_data = daily_total[daily_total['USE_YMD'].dt.date == current_date].iloc[0]
    current_total = current_data['total']
    
    rates = {}
    
    # 전주대비 (동일 요일)
    week_ago = get_same_weekday_date(current_date, 7)
    week_ago_data = daily_total[daily_total['USE_YMD'].dt.date == week_ago]
    if not week_ago_data.empty:
        week_ago_total = week_ago_data.iloc[0]['total']
        rates['전주대비'] = ((current_total - week_ago_total) / week_ago_total * 100)
    
    # 전월대비 (4주 전, 동일 요일)
    month_ago = get_same_weekday_date(current_date, 28)
    month_ago_data = daily_total[daily_total['USE_YMD'].dt.date == month_ago]
    if not month_ago_data.empty:
        month_ago_total = month_ago_data.iloc[0]['total']
        rates['전월대비'] = ((current_total - month_ago_total) / month_ago_total * 100)
    
    # 전년대비 (52주 전 또는 53주 전, 동일 요일)
    # 윤년을 고려하여 364일(52주) 또는 371일(53주) 전의 같은 요일을 찾음
    year_ago = get_same_weekday_date(current_date, 364)
    if calendar.isleap(current_date.year - 1):
        year_ago = get_same_weekday_date(current_date, 371)
    
    year_ago_data = daily_total[daily_total['USE_YMD'].dt.date == year_ago]
    if not year_ago_data.empty:
        year_ago_total = year_ago_data.iloc[0]['total']
        rates['전년대비'] = ((current_total - year_ago_total) / year_ago_total * 100)
    
    return rates

def convert_df_to_csv(df):
    """DataFrame을 CSV 문자열로 변환합니다."""
    return df.to_csv(index=True).encode('utf-8-sig')  # UTF-8 with BOM for Excel

if api_key and station_name and start_date <= end_date:
    # 전체 기간의 데이터 수집
    all_data = []
    current_date = start_date
    
    # 증감률 계산 여부 선택
    show_rates = st.checkbox("증감률 계산하기", value=False)
    
    # 증감률 계산을 위한 추가 데이터 수집 범위 설정
    if show_rates:
        earliest_date = min(
            start_date - timedelta(days=371),  # 윤년 고려
            start_date - timedelta(days=28)    # 월간 비교
        )
    else:
        earliest_date = start_date
    
    with st.spinner('데이터를 수집하고 있습니다...'):
        while current_date <= end_date:
            daily_data = fetch_data(current_date, station_name)
            for row in daily_data:
                row['USE_YMD'] = pd.to_datetime(row['USE_YMD'])
            all_data.extend(daily_data)
            current_date += timedelta(days=1)

    if all_data:
        # DataFrame 생성 및 전처리
        df = pd.DataFrame(all_data)
        df["GTON_TNOPE"] = df["GTON_TNOPE"].astype(float)
        df["GTOFF_TNOPE"] = df["GTOFF_TNOPE"].astype(float)
        
        # 전체 승하차 인원 트렌드
        st.header("📊 전체 승하차 인원 트렌드")
        
        # 일별 전체 승하차 인원 계산
        daily_total = df.groupby('USE_YMD').agg({
            'GTON_TNOPE': 'sum',
            'GTOFF_TNOPE': 'sum'
        }).reset_index()
        
        # 전체 승하차 인원 그래프
        total_chart_data = pd.DataFrame({
            '날짜': daily_total['USE_YMD'].dt.strftime('%Y-%m-%d'),
            '승차인원': daily_total['GTON_TNOPE'],
            '하차인원': daily_total['GTOFF_TNOPE']
        })
        
        total_chart_melted = pd.melt(
            total_chart_data,
            id_vars=['날짜'],
            value_vars=['승차인원', '하차인원'],
            var_name='구분',
            value_name='인원'
        )
        
        st.bar_chart(
            data=total_chart_melted,
            x='날짜',
            y='인원',
            color='구분',
            height=400
        )
        
        # 전체 통계 지표
        total_on = daily_total['GTON_TNOPE'].sum()
        total_off = daily_total['GTOFF_TNOPE'].sum()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("총 승차인원", f"{int(total_on):,}명")
        with col2:
            st.metric("총 하차인원", f"{int(total_off):,}명")
        with col3:
            st.metric("총 이용객", f"{int(total_on + total_off):,}명")
        
        # 증감률 계산 및 표시 (선택적)
        if show_rates and len(daily_total) > 1:
            latest_date = daily_total['USE_YMD'].max().date()
            rates = calculate_change_rates(df, latest_date)
            
            st.subheader("📈 증감률")
            rate_cols = st.columns(len(rates))
            for col, (period, rate) in zip(rate_cols, rates.items()):
                delta_color = "normal" if abs(rate) < 5 else ("off" if rate < 0 else "inverse")
                col.metric(
                    period,
                    f"{rate:.1f}%",
                    delta_color=delta_color
                )
        
        # 전체 데이터 CSV 다운로드
        total_data_df = df.copy()
        total_data_df['USE_YMD'] = total_data_df['USE_YMD'].dt.strftime('%Y-%m-%d')
        total_data_df = total_data_df.rename(columns={
            'USE_YMD': '날짜',
            'SBWY_ROUT_LN_NM': '호선명',
            'SBWY_STNS_NM': '역명',
            'GTON_TNOPE': '승차인원',
            'GTOFF_TNOPE': '하차인원'
        })
        total_data_df = total_data_df[['날짜', '호선명', '역명', '승차인원', '하차인원']]
        
        st.download_button(
            label="📥 전체 데이터 다운로드",
            data=convert_df_to_csv(total_data_df),
            file_name=f"{station_name}_전체_{start_date}_{end_date}.csv",
            mime="text/csv"
        )
        
        st.divider()
        
        # 호선별 상세 데이터
        st.header("🚇 호선별 상세 데이터")
        
        # 호선별로 그룹화
        lines = df["SBWY_ROUT_LN_NM"].unique()
        
        for line in lines:
            st.subheader(f"{line}")
            
            # 호선별 데이터 필터링
            line_data = df[df["SBWY_ROUT_LN_NM"] == line].copy()
            line_data = line_data.sort_values('USE_YMD')  # 날짜순 정렬
            
            # 막대 그래프 생성
            chart_data = pd.DataFrame({
                '날짜': line_data['USE_YMD'].dt.strftime('%Y-%m-%d'),
                '승차인원': line_data['GTON_TNOPE'],
                '하차인원': line_data['GTOFF_TNOPE']
            })
            
            chart_data_melted = pd.melt(
                chart_data,
                id_vars=['날짜'],
                value_vars=['승차인원', '하차인원'],
                var_name='구분',
                value_name='인원'
            )
            
            # 그래프 표시
            st.bar_chart(
                data=chart_data_melted,
                x='날짜',
                y='인원',
                color='구분',
                height=400
            )
            
            # 통계 지표
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("평균 승차인원", f"{int(line_data['GTON_TNOPE'].mean()):,}명")
            with col2:
                st.metric("평균 하차인원", f"{int(line_data['GTOFF_TNOPE'].mean()):,}명")
            with col3:
                total_passengers = int(line_data['GTON_TNOPE'].sum() + line_data['GTOFF_TNOPE'].sum())
                st.metric("총 이용객", f"{total_passengers:,}명")
            
            # 데이터 테이블 표시
            st.caption("📊 상세 데이터")
            display_df = chart_data.set_index('날짜')
            
            # 천 단위 구분 기호 추가
            for col in ['승차인원', '하차인원']:
                display_df[col] = display_df[col].map(lambda x: f"{int(x):,}")
            
            st.dataframe(display_df, use_container_width=True)
            
            # 호선별 CSV 다운로드
            line_data_df = chart_data.copy()
            st.download_button(
                label=f"📥 {line} 데이터 다운로드",
                data=convert_df_to_csv(line_data_df),
                file_name=f"{station_name}_{line}_{start_date}_{end_date}.csv",
                mime="text/csv"
            )
            
            st.divider()  # 구분선 추가
            
    else:
        st.error("데이터를 찾을 수 없습니다.")
elif start_date > end_date:
    st.error("종료일은 시작일보다 이후여야 합니다.")

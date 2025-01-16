import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import numpy as np
import talib
from fisa_quant.pages.auth import *

st.set_page_config(layout="wide")

# 대표 사이트 명
st.title(' 🏦 우리 FISA TA 🏦')

# Streamlit 제목 설정
st.subheader('💵 실시간 주식 종목 분석')

# 사용자로부터 종목명, 종목코드 또는 티커 입력 받기
ticker_input = st.text_input('🧐 종목코드 또는 종목 티커를 입력하세요:', 'AAPL')
st.session_state.ticker = ticker_input

# 주식 데이터를 FinanceDataReader를 통해 가져오기
ticker = ticker_input if not ticker_input.isdigit() else ticker_input
start_date = (datetime.date.today() - datetime.timedelta(days=365 * 1.5)).strftime('%Y-%m-%d')  # 최소 1년 전 데이터 확보
data = fdr.DataReader(ticker, start=start_date)

# 실시간 주가 표시
st.subheader('💁🏻 실시간 주가')
st.write(f'현재가: {np.round(data.iloc[-1]["Close"], 0)}')
st.write(f'전날 종가: {np.round(data.iloc[-2]["Close"], 0)}')
st.write(f'최고가: {np.round(data["Close"].max(), 0)}')
st.write(f'최저가: {np.round(data["Close"].min(), 0)}')

if st.button('관심종목 등록'):
    if ('authentication_status' in st.session_state) and ('name' in st.session_state):
        if 'like' in config['credentials']['usernames'][st.session_state["name"]]:
            config['credentials']['usernames'][st.session_state["name"]]['like'].append(ticker)
        else:
            config['credentials']['usernames'][st.session_state["name"]]['like'] = [ticker]
    else:
        st.write("관심종목 등록은 로그인이 필요합니다.")

# 과거 데이터 표시
st.subheader('💁🏻 종목 히스토리')
st.dataframe(data, width=1200)

# Moving Average 및 거래량 계산
short_ma = st.slider('단기 이동평균선 기간 설정', 5, 50, 20)
long_ma = st.slider('장기 이동평균선 기간 설정', 50, 200, 100)

data['Short_MA'] = data['Close'].rolling(window=short_ma).mean()
data['Long_MA'] = data['Close'].rolling(window=long_ma).mean()
data = data[data.index.dayofweek < 5]
# 유효 데이터로 필터링 (장기 MA가 계산된 이후 구간만 포함)
valid_data = data.dropna(subset=['Long_MA'])

# Bar Chart 및 보조지표(이동평균선, 거래량) 시각화
st.subheader('📊 실시간 주식 차트 (Technical Overview)')

# 캔들차트 (Candlestick Chart) 설정
fig = make_subplots(specs=[[{"secondary_y": True}]])
data = data[data.index.dayofweek < 5]
# 캔들차트: 상승(양봉)과 하락(음봉)을 색으로 구분
fig.add_trace(go.Candlestick(
    x=valid_data.index,
    open=valid_data['Open'], high=valid_data['High'],
    low=valid_data['Low'], close=valid_data['Close'],
    increasing_line_color='red', decreasing_line_color='blue',
    name="Candlestick"), secondary_y=False)

# 이동평균선 추가 (단기, 장기)
fig.add_trace(go.Scatter(
    x=valid_data.index, y=valid_data['Short_MA'],
    line=dict(color='orange', width=2), name=f'{short_ma}일 단기 이동평균선'), secondary_y=False)

fig.add_trace(go.Scatter(
    x=valid_data.index, y=valid_data['Long_MA'],
    line=dict(color='blue', width=2), name=f'{long_ma}일 장기 이동평균선'), secondary_y=False)

# 거래량 추가 (Bar chart)
valid_data['Volume_Color'] = np.where(valid_data['Close'] > valid_data['Close'].shift(1), 'red', 'blue')

# 거래량 추가 (Bar chart)
fig.add_trace(go.Bar(
    x=valid_data.index,
    y=valid_data['Volume'],
    name='거래량',
    marker=dict(color=valid_data['Volume_Color']),  # 색상 지정
    opacity=1  # 투명도를 1로 설정하여 더 선명하게 표시
), secondary_y=True)


# 차트 레이아웃 설정
fig.update_layout(
    title=f'{ticker} 주식 차트',
    xaxis_title='날짜',
    yaxis_title='가격',
    template='plotly_dark',  # 어두운 테마 설정
    xaxis_rangeslider_visible=False,
    height=700  # 차트 크기 조정
)
max_volume = valid_data['Volume'].max()
fig.update_yaxes(title_text="거래량", secondary_y=True, range = [0, max_volume * 4])

# 차트 Streamlit에 표시
st.plotly_chart(fig)

# Bollinger Bands 및 RSI 계산
bollinger_period = st.slider('Bollinger Bands 기간 설정', 10, 50, 20)
rsi_period = st.slider('RSI 기간 설정', 10, 50, 14)

# Bollinger Bands 계산
data['upper_band'], data['middle_band'], data['lower_band'] = talib.BBANDS(
    data['Close'], timeperiod=bollinger_period, nbdevup=2, nbdevdn=2, matype=0)

# RSI 계산
data['rsi'] = talib.RSI(data['Close'], timeperiod=rsi_period)

# Bollinger Bands와 RSI 기반 의견
bollinger_opinion = ''
rsi_opinion = ''

if data['Close'].iloc[-1] > data['upper_band'].iloc[-1]:
    bollinger_opinion = '하락 가능성 (상단 터치)'
elif data['Close'].iloc[-1] < data['lower_band'].iloc[-1]:
    bollinger_opinion = '상승 가능성 (하단 터치)'

if data['rsi'].iloc[-1] > 70:
    rsi_opinion = '과매수 (하락 가능성)'
elif data['rsi'].iloc[-1] < 30:
    rsi_opinion = '과매도 (상승 가능성)'

# 종합 분석
st.subheader('⭐️ 종합 분석 결과')

# 현재 주식 가격에 대한 Bollinger Bands 의견
st.write(f'현재 주식 가격에 대한 Bollinger Bands 의견: {bollinger_opinion}')

# 현재 주식 가격에 대한 RSI 의견
st.write(f'현재 주식 가격에 대한 RSI 의견: {rsi_opinion}')

# 주간 평균 변화율 계산
data['Weekly_Change'] = data['Close'].pct_change(periods=5) * 100  # 5일 기준 (1주일)
weekly_change = data['Weekly_Change'].iloc[-1]

if weekly_change > 0:
    weekly_change_opinion = '상승세'
else:
    weekly_change_opinion = '하락세'

st.write(f'최근 1주일 평균 변화율: {weekly_change:.2f}% ({weekly_change_opinion})')

# 현재 추세 판단 (MA 교차)
if data['Short_MA'].iloc[-1] > data['Long_MA'].iloc[-1]:
    trend_opinion = '상승 추세 (골든 크로스 발생)'
elif data['Short_MA'].iloc[-1] < data['Long_MA'].iloc[-1]:
    trend_opinion = '하락 추세 (데드 크로스 발생)'
else:
    trend_opinion = '중립 추세'

st.write(f'현재 추세: {trend_opinion}')

# 변동성 (Bollinger Bands 폭)
volatility = (data['upper_band'] - data['lower_band']).iloc[-1]
st.write(f'현재 변동성 (Bollinger Bands 폭): {volatility:.2f}')

# 투자 의견 (종합)
if bollinger_opinion == '상승 가능성 (하단 터치)' and rsi_opinion == '과매도 (상승 가능성)':
    investment_opinion = '상승 가능성이 높아 매수 추천'
elif bollinger_opinion == '하락 가능성 (상단 터치)' and rsi_opinion == '과매수 (하락 가능성)':
    investment_opinion = '하락 가능성이 높아 매도 추천'
else:
    investment_opinion = '추세를 더 확인 후 결정 필요'

st.write(f'투자 의견: {investment_opinion}')

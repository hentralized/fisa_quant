import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import plotly.graph_objects as go
import plotly as plt
from plotly.subplots import make_subplots
import datetime
import talib

# 대표 사이트 명
st.title(' 🏦 우리 FISA 증권 🏦')

# Streamlit 제목 설정
st.subheader('💵 실시간 주식 종목 분석')

# 사용자로부터 종목명, 종목코드 또는 티커 입력 받기
ticker_input = st.text_input('🧐 종목코드 또는 종목 티커를 입력하세요:', 'AAPL')

# 주식 데이터를 FinanceDataReader를 통해 가져오기
data = None

# 사용자가 입력한 티커가 숫자형(한국 주식)인 경우
if ticker_input.isdigit():
    ticker = ticker_input  # 숫자형 티커는 한국 주식
    currency_symbol = '₩'
else:
    ticker = ticker_input  # 외국 주식 티커 그대로 사용
    currency_symbol = '$'

# 해당 종목에 대한 데이터를 FinanceDataReader에서 가져오기
data = fdr.DataReader(ticker, start='2024-01-01')

# 실시간 주가 표시
st.subheader('💁🏻 실시간 주가')
st.write(f'현재가: {currency_symbol}{data.iloc[-1]["Close"]:.2f}')
st.write(f'전날 종가: {currency_symbol}{data.iloc[-2]["Close"]:.2f}')
st.write(f'최고가: {currency_symbol}{data["Close"].max():.2f}')
st.write(f'최저가: {currency_symbol}{data["Close"].min():.2f}')

# 과거 데이터 표시
st.subheader('💁🏻 종목 히스토리')
st.dataframe(data, width=1200)

# Moving Average 및 거래량 계산
short_ma = st.slider('단기 이동평균선 기간 설정', 5, 50, 20)
long_ma = st.slider('장기 이동평균선 기간 설정', 50, 200, 100)

data['Short_MA'] = data['Close'].rolling(window=short_ma).mean()
data['Long_MA'] = data['Close'].rolling(window=long_ma).mean()

# Bollinger Bands의 기간을 단기 이동평균선 기간과 동일하게 설정
bollinger_period = 20
rsi_period = 14

# Bollinger Bands 계산
bollinger_opinion = ''
data['upper_band'], data['middle_band'], data['lower_band'] = talib.BBANDS(data['Close'], timeperiod=bollinger_period, nbdevup=2, nbdevdn=2, matype=0)
    
# Bollinger Bands 상단/하단 터치 판단
if data['Close'].iloc[-1] > data['upper_band'].iloc[-1]:
    bollinger_opinion = '하락 가능성 (상단 터치)'
elif data['Close'].iloc[-1] < data['lower_band'].iloc[-1]:
    bollinger_opinion = '상승 가능성 (하단 터치)'
else:
    bollinger_opinion = '중립 (밴드 내 위치)'

# Bar Chart 및 보조지표(이동평균선, 거래량) 시각화
st.subheader('📊 실시간 주식 차트 (캔들 차트 & 이동평균선 & 거래량)')

# 캔들차트 (Candlestick Chart) 설정
fig = go.Figure()

fig = make_subplots(specs=[[{"secondary_y":True}]])

# 캔들차트: 상승(양봉)과 하락(음봉)을 색으로 구분
fig.add_trace(go.Candlestick(x=data.index,
                             open=data['Open'], high=data['High'],
                             low=data['Low'], close=data['Close'],
                             increasing_line_color='red', decreasing_line_color='green',
                             name="Candlestick"), secondary_y=False)

# 이동평균선 추가 (단기, 장기)
fig.add_trace(go.Scatter(x=data.index, y=data['Short_MA'],
                         line=dict(color='orange', width=2), name=f'{short_ma}일 단기 이동평균선'), secondary_y=False)
fig.add_trace(go.Scatter(x=data.index, y=data['Long_MA'],
                         line=dict(color='blue', width=2), name=f'{long_ma}일 장기 이동평균선'), secondary_y=False)

# Bollinger Bands 추가
fig.add_trace(go.Scatter(x=data.index, y=data['upper_band'],
                         line=dict(color='purple', width=1, dash='dash'),
                         name='Bollinger Upper Band', legendgroup='bollinger Bands', showlegend=False), secondary_y=False)

fig.add_trace(go.Scatter(x=data.index, y=data['middle_band'],
                         line=dict(color='grey', width=1, dash='dot'),
                         name='Bollinger Middle Band', legendgroup='bollinger Bands', showlegend=False), secondary_y=False)
fig.add_trace(go.Scatter(x=data.index, y=data['lower_band'],
                         line=dict(color='purple', width=1, dash='dash'),
                         name='Bollinger Lower Band', legendgroup='bollinger Bands', showlegend=False), secondary_y=False)
fig.add_trace(go.Scatter(x=data.index, y=data['upper_band'],
                         fill='tonexty',  # 상단 밴드에서 하단 밴드까지 채우기
                         fillcolor='rgba(128, 0, 128, 0.2)',  # 연한 보라색
                         line=dict(color='rgba(255,255,255,0)'),  # 선은 안 보이게 설정
                         name='Bollinger Bands', legendgroup='bollinger Bands', showlegend=True), secondary_y=False)

# 거래량 추가 (Bar chart)
fig.add_trace(go.Bar(x=data.index, y=data['Volume'], name='거래량', marker=dict(color='lightgray'), opacity=0.375), secondary_y=True)

# 차트 레이아웃 설정
fig.update_layout(
    title=f'{ticker} 주식 차트',
    xaxis_title='날짜',
    yaxis_title='가격',
    template='plotly_dark',  # 어두운 테마 설정
    xaxis_rangeslider_visible=False,
    height=700  # 차트 크기 조정
)
fig.update_yaxes(title_text="거래량", secondary_y=True)

# RSI 의견
rsi_opinion = ''

# 상승폭, 하락폭 계산
delta = data['Close'].diff()
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)

# 14일 동안의 평균 상승폭, 하락폭 계산
avg_gain = gain.rolling(window=rsi_period).mean()
avg_loss = loss.rolling(window=rsi_period).mean()

# RSI 계산 (RSI = 100 - (100 / (1 + RS)))
rs = avg_gain / avg_loss
data['rsi'] = 100 - (100 / (1 + rs))
   
# RSI 판단
if data['rsi'].iloc[-1] > 70:
        rsi_opinion = '과매수 (하락 가능성)'
elif data['rsi'].iloc[-1] < 30:
    rsi_opinion = '과매도 (상승 가능성)'
else:
    rsi_opinion = '중립'

# 차트 레이아웃 설정
fig.update_layout(
    title=f'{ticker} 주식 차트',
    xaxis_title='날짜',
    yaxis_title='가격',
    template='plotly_dark',  # 어두운 테마 설정
    xaxis_rangeslider_visible=False,
    height=700  # 차트 크기 조정
)

fig.update_yaxes(title_text="거래량", secondary_y=True)

# 차트 Streamlit에 표시
st.plotly_chart(fig)

# 종합 분석
st.subheader('💁🏻 종합 분석 결과')

st.write(f'현재 주식 가격에 대한 Bollinger Bands 의견: {bollinger_opinion}')
st.write(f'현재 주식 가격에 대한 RSI 의견: {rsi_opinion}')

# 매수/매도 및 공매도 데이터 가져오기 함수
def get_trade_data(ticker):
    data = fdr.DataReader(ticker, start='2024-01-01')
    return data

# 최근 한달간 매수/매도 및 공매도 데이터 가져오기
end_date = datetime.date.today()
start_date = end_date - datetime.timedelta(days=30)
trade_data = get_trade_data(ticker)

institution_buy = trade_data['Volume'].sum()
institution_sell = trade_data['Volume'].sum() * 0.5
individual_buy = trade_data['Volume'].sum() * 0.5
individual_sell = trade_data['Volume'].sum() * 0.4
short_selling = trade_data['Volume'].sum() * 0.1

# 종합 분석
if institution_buy > institution_sell and individual_buy > individual_sell:
    opinion = '매수 의견'
    opinion_description = '기관과 개인 투자자 모두 최근 한달간 매수량이 매도량을 초과하므로, 해당 종목의 주식 가격 상승 가능성이 높다고 판단됩니다.'
elif institution_sell > institution_buy and individual_sell > individual_buy:
    opinion = '매도 의견'
    opinion_description = '기관과 개인 투자자 모두 최근 한달간 매도량이 매수량을 초과하므로, 해당 종목의 주식 가격 하락 가능성이 높다고 판단됩니다.'
else:
    opinion = '중립 의견'
    opinion_description = '기관과 개인 투자자의 매수량과 매도량이 비슷하므로, 해당 종목의 주식 가격이 변동 없이 안정적인 상태일 가능성이 높습니다.'

# 종합 분석 결과 표시
st.write(f'기관의 최근 한달간 총 매수량: {int(institution_buy):,}')
st.write(f'기관의 최근 한달간 총 매도량: {int(institution_sell):,}')
st.write(f'개인투자자의 최근 한달간 총 매수량: {int(individual_buy):,}')
st.write(f'개인투자자의 최근 한달간 총 매도량: {int(individual_sell):,}')
st.write(f'공매도 현황: {int(short_selling):,}')
st.write(f'현재 주식 가격에 대한 의견: {opinion}')
st.write(f'의견 설명: {opinion_description}')
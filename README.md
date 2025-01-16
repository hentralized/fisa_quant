## 🙌 안녕하세요. 🏦 우리FISA TA 입니다!!

## ❓ 우리FISA TA가 뭐예요?
- **우리FISA 증권**은 **<u>우리FISA AI엔지니어링과정 교육생 4명이 함께 투자자산을 더 쉽게 조회하고 종목을 검색</u>** 하기 위해 만들었어
<br>

- 종목명 또는 티커를 입력하시면 해당 종목에 관한 **재무제표, 실시간 차트, 기관투자사의 매수 및 매도량을 추적** 할 수 있어요.
<br>

- **MA, RSI, Bollinger Bands 등** 다양한 보조지표를 활용하여 <u>**Technical Analysis**</u> 을 사용자에게 제공합니다.
<br>

- 종합분석결과 및 재무제표를 직접 확인해보고 **스스로의 관점 또한 도출 할 수 있습니다.**

## 🙋‍♀️ 좀 더 구체적으로 가르쳐주세요!   
```
import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import talib
import streamlit.components.v1 as components
import datetime
```
<br>

**1. Streamlit**
- streamlit 모듈을 사용해 가상환경으로 심플한 디자인의 필요한것만 담은 증권 정보 웹페이지를 구현했습니다.

 <br>

**2. FDR(FinanceDataReader)**

- 국내 증시에 상장된 'KRX', 'KOSPI', 'KODAQ', 'KONEX' 를 리스팅 할 수 있습니다.
- 해외 증시에 상장된 'NASDAQ', 'NYSE', 'AMEX', 'S&P500', 'SSE'(상해), 'SZSE'(심천), 'HKEX'(홍콩), 'TSE'(도쿄)를 리스팅 할 수 있습니다.
- <u>ETF Symbol listings:</u>  'ETF/KR' ETF를 리스팅 할 수 있습니다.
- <u>Stock price(개별종목 가격 데이터):</u> '005930'(Samsung), '091990'(Celltrion Healthcare) ...
- <u>Stock price(해외 거래소 개별종목 가격 데이터):</u> 'AAPL', 'AMZN', 'GOOG' ... (you can specify exchange(market) and symbol)
- <u>Indexes:</u> 'KS11'(코스피지수), 'KQ11'(코스닥지수), 'DJI'(다우존스지수), 'IXIC'(나스닥지수), 'US500'(S&P 500지수) 를 불러올 수 있습니다.
- <u>Exchanges:</u> 'USD/KRW', 'USD/EUR', 'CNY/KRW' 등 조합가능한 화폐별 환율 데이터 일자별 데이터를 함께 불러올 수 있습니다.
- <u>Cryptocurrency price data:</u> 'BTC/USD', 'ETH/KRW' 등 암호화폐 가격 데이터를 불러올 수 있습니다.

<br> 

**3. TA-Lib**
- 다양한 기술적 지표: 이동 평균, 상대 강도 지수(RSI), 볼린저 밴드, MACD 등을 비롯한 150개 이상의 기술적 지표 제공.
- 유연한 데이터 처리: 다양한 형태의 시계열 데이터에 대한 기술적 지표 계산을 지원합니다.
- 효율적인 성능: 대량의 금융 데이터에 대해 빠르게 기술적 지표를 계산할 수 있도록 최적화되어 있습니다.
- 통합성: Pandas, NumPy와 같은 Python 데이터 분석 라이브러리와 잘 통합되어 사용할 수 있습니다.

<br>  

## 🛠 기능 엿보기   

1. [❓ 우리FISA TA가 뭐예요?  ](#-easymemd가-뭐예요)
2. [🙋‍♀️ Main Page](#-좀-더-구체적으로-가르쳐주세요)
3. [🛠 기능 엿보기](#-기능-엿보기)
    - [Header](#header)   
    - [Text Style1](#text-style1)   
    - [Text Stlye2](#text-style2)   
    - [List](#list)      
    - [Link](#link)   
    - [Code Block](#code-block)   
    - [Table](#table)   

<br>   

## 🔗 Link   
### General link
- [🚗 Visit 우리FISA TA Repo](https://github.com/MINJAEKH/fisa_quant)   
- [🙋‍♂️ Visit 우리FISA 공식 홈페이지](https://woorifisa.com/)

### Image link
![우리FISA](https://github.com/user-attachments/assets/aa4f6b8b-aae1-4b9f-a37a-b98c471a7d46)

## 💫 어려웠던 점 
1. ta-lib 라이브러리 설치 중 dependency 충돌이 발생했어요. 
2. API key를 사용하여 재무제표 이외으 기업의 정보를 가져오지 못해 아쉬워요 


import FinanceDataReader as fdr
import FinanceDataReader.naver as fdrn
import yfinance as yf

from datetime import datetime
import numpy as np
import pandas as pd

# 분기별 종료 날짜 계산 함수
def get_end_date(year, quarter):
    quarter_end_months = {1: "12-31", 2: "03-31", 3: "06-30", 4: "09-30"}
    if quarter == 1:
        return pd.to_datetime(f"{year-1}-{quarter_end_months[quarter]}")
    return pd.to_datetime(f"{year}-{quarter_end_months[quarter]}")

remain_columns =['매출액', '영업이익','당기순이익','자산총계', '부채총계', '자본총계','ROE(%)', 'ROA(%)', '부채비율','PER(배)','PBR(배)']

def fs_domestic(ticker) :
    today = datetime.now()

    # 최근 3개의 분기별 데이터 가져오기
    current_quarter = (today.month - 1) // 3 + 1
    quarter_df = fdrn.snap.finstate_summary(ticker, fin_type='0', freq='Q')

    quarter_df['Date'] = quarter_df.index # 인덱스 초기화
    quarter_df.reset_index(drop=True, inplace=True)

    end_date = get_end_date(today.year, current_quarter)
    quarter_df = quarter_df[quarter_df['Date'] <= end_date].tail(3)

    date_columns = quarter_df['Date'].dt.strftime('%Y-%m-%d')
    quarter_df = quarter_df[remain_columns]
    quarter_df = quarter_df.T
    quarter_df.columns = date_columns

    # 연간 데이터
    year_df = fdrn.snap.finstate_summary(ticker, fin_type='0', freq='Y')
    year_df['Date'] = year_df.index # 인덱스 초기화
    year_df.reset_index(drop=True, inplace=True)

    year = today.year - 1
    year_df = year_df[year_df['Date'].dt.year <= 2023].tail(3)

    date_columns = year_df['Date'].dt.strftime('%Y-%m-%d')
    year_df = year_df[remain_columns]
    year_df = year_df.T
    year_df.columns = date_columns

    df = pd.concat([year_df, quarter_df], axis =1)
    columns = pd.MultiIndex.from_tuples(
    [("연간", col) if idx < 3 else ("분기", col) for idx, col in enumerate(df.columns)]
    )
    df.columns = columns
    df.index.name = None

    return df

def fs_global(ticker):
    apple = yf.Ticker(ticker)
    apple

    af1 = apple.financials.loc[['Total Revenue', 'Operating Income', 'Net Income'], :]#['2022-09-30', '2023-09-30', '2024-09-30']]
    af1 = af1.iloc[:,:3]
    af1 = af1.iloc[:,::-1]
    af2 = apple.quarterly_financials.loc[['Total Revenue', 'Operating Income', 'Net Income'], :]# ['2024-03-31', '2024-06-30', '2024-09-30']]
    af2 = af2.iloc[:,:3]
    af2 = af2.iloc[:,::-1]
    af = pd.concat([af1, af2], axis=1)

    abs = apple.balance_sheet.loc[['Total Assets', 'Total Liabilities Net Minority Interest'], :]# ['2022-09-30', '2023-09-30', '2024-09-30']]
    abs = abs.iloc[:,:3]
    abs = abs.iloc[:,::-1]
    abs = abs.T
    abs['자본총계'] = abs['Total Assets'] - abs['Total Liabilities Net Minority Interest']
    abs = abs.T

    absq = apple.quarterly_balance_sheet.loc[['Total Assets', 'Total Liabilities Net Minority Interest'], :]# ['2024-03-31', '2024-06-30', '2024-09-30']]
    absq = absq.iloc[:,:3]
    absq = absq.iloc[:,::-1]
    absq = absq.T
    absq['자본총계'] = absq['Total Assets'] - absq['Total Liabilities Net Minority Interest']
    absq = absq.T

    ab = pd.concat([abs, absq], axis=1)

    r = pd.concat([af, ab]).T.astype('Int64')
    r['ROA(%)'] = round(r['Net Income'] / r['Total Assets'] * 100, 1)
    r['ROE(%)'] = round(r['Net Income'] / r['자본총계'] * 100, 1)
    r['부채비율'] = round(r['Total Liabilities Net Minority Interest'] / r['자본총계'] * 100, 2)
    r['PER(배)'] = round(apple.info['marketCap'] / r['Net Income'], 2)
    r['PBR(배)'] = round(apple.info['marketCap'] / r['Total Assets'], 2)
    r.columns = ['매출액', '영업이익','당기순이익','자산총계', '부채총계', '자본총계', 'ROE(%)', 'ROA(%)', '부채비율','PER(배)','PBR(배)']
    r = r.T
    column_list = r.columns
    multi_index = pd.MultiIndex.from_tuples(
        [("연간", column_list[0].strftime('%Y-%m-%d')), ("연간", column_list[1].strftime('%Y-%m-%d')), ("연간", column_list[2].strftime('%Y-%m-%d')),
        ("분기", column_list[3].strftime('%Y-%m-%d')), ("분기", column_list[4].strftime('%Y-%m-%d')), ("분기", column_list[5].strftime('%Y-%m-%d'))]
    )
					
# 컬럼에 멀티인덱스 적용
    r.columns = multi_index
    return r
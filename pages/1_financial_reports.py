import sys
from pathlib import Path

import pandas as pd
import numpy as np
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent))

from get_financial_reports import fs_global, fs_domestic
from utils import show_bar_chart, get_triangle

st.set_page_config(layout="wide")

# 사이드바 설정
st.sidebar.title("Financial Reports")

# "검색 초기화하기" 버튼 클릭 시 모든 상태 초기화
if st.sidebar.button("검색 초기화하기"):
    st.session_state.clear()

# 종목 코드 입력
if 'ticker' not in st.session_state:
    st.session_state['ticker'] = ""  # 초기화

ticker = st.sidebar.text_input("종목코드를 입력해주세요", st.session_state['ticker'])

# 실적 옵션 상태 관리
if 'view_option' not in st.session_state:
    st.session_state['view_option'] = "분기실적"  # 기본값: 분기실적

# 데이터 상태 관리
if 'financial_data' not in st.session_state:
    st.session_state['financial_data'] = None  # 초기화

# 재무제표 조회 버튼
if st.sidebar.button("재무제표 조회하기"):
    if ticker.isdigit():  # 한국 종목
        df = fs_domestic(ticker)
    else:
        df = fs_global(ticker)

    if df is not None :
        st.session_state['financial_data'] = df  # 데이터를 상태에 저장
    else:
        st.sidebar.warning("재무제표를 조회할 수 없습니다. 종목 코드를 다시 확인해 주세요.")

# 데이터가 존재하는 경우만 표시
if st.session_state['financial_data'] is not None:
    # 실적 보기 옵션 
    st.session_state['view_option'] = st.sidebar.radio(
        "실적 보기 옵션을 선택하세요:",
        options=["분기실적", "연간실적"],
        index=0 if st.session_state['view_option'] == "분기실적" else 1,
    )

    # 선택한 실적 옵션에 따라 필터링
    df = st.session_state['financial_data']
    if st.session_state['view_option'] == "연간실적":
        filtered_df = df.iloc[:, :3]  # 연간실적 
    else:
        filtered_df = df.iloc[:, -3:]  # 분기실적 
    
    # 변화량 계산
    if filtered_df.shape[1] > 1:  
        latest_values = filtered_df.iloc[:, -1]  # 마지막 컬럼 값 (가장 최근 데이터)
        previous_values = filtered_df.iloc[:, -2]  # 바로 이전 컬럼 값
        changes = latest_values - previous_values  # 변화량

        col_name = f"이전 {st.session_state['view_option']} 변화량"
        
        results = pd.DataFrame({
            "항목": filtered_df.index,
            f"최근 {st.session_state['view_option']}": latest_values.values,
<<<<<<< HEAD:차민재/pages/1_financial_reports.py
            f"{col_name}": np.round(changes.values, 2)
=======
            f"{col_name}": np.round(changes.values, 2) if changes.dtype == 'float64' else changes.values

>>>>>>> 2ad79c146f30941ba622bef0ffbb83794ee4f87e:pages/1_financial_reports.py
        })

        # 변화량에 따라 색상 지정
        def format_changes(row):
            if row[col_name] > 0:
                return f"<span style='color:red;'>+{row[col_name]:,}</span>"  # 빨간색
            elif row[col_name] < 0:
                return f"<span style='color:blue;'>{row[col_name]:,}</span>"  # 파란색
            else:
                return f"{row[col_name]:,}"  # 기본값

        results[col_name] = results.apply(format_changes, axis=1)

        col1, col2, col3, col4 = st.columns(4)
        with col1 :
            value, answer = get_triangle(filtered_df, 'ROE(%)')
            st.markdown(f"<h4 style='text-align: center;'>ROE</h3>", unsafe_allow_html=True)
            st.markdown(f"<h5 style='text-align: center;'>{value}</h3>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align: center;'>{answer}</h3>", unsafe_allow_html=True)
        with col2 :
            value, answer = get_triangle(filtered_df, 'ROA(%)')
            st.markdown(f"<h4 style='text-align: center;'>ROA</h3>", unsafe_allow_html=True)
            st.markdown(f"<h5 style='text-align: center;'>{value}</h3>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align: center;'>{answer}</h3>", unsafe_allow_html=True)
        with col3 :
            value, answer = get_triangle(filtered_df, 'PER(배)')
            st.markdown(f"<h4 style='text-align: center;'>PER</h3>", unsafe_allow_html=True)
            st.markdown(f"<h5 style='text-align: center;'>{value}</h3>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align: center;'>{answer}</h3>", unsafe_allow_html=True)
        with col4 :
            value, answer = get_triangle(filtered_df, 'PBR(배)')
            st.markdown(f"<h4 style='text-align: center;'>PBR</h3>", unsafe_allow_html=True)
            st.markdown(f"<h5 style='text-align: center;'>{value}</h3>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align: center;'>{answer}</h3>", unsafe_allow_html=True)
        
        st.markdown("<hr style='border: 1px solid #ccc; width: 100%; margin: auto;'/>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = show_bar_chart(filtered_df, ['매출액','영업이익','당기순이익'], title = '손익계산서 지표 비교')
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown(f"<h4 style='text-align: center;'>최근 {st.session_state['view_option']} 비교 변화</h3>", unsafe_allow_html=True)
            st.write(
                results.to_html(escape=False, index=False),
                unsafe_allow_html=True
            )

        with col2:
            fig = show_bar_chart(filtered_df, ['자산총계','부채총계','자본총계'], title = '재무상태표 지표 비교')
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("<h4 style='text-align: center;'>재무제표</h3>", unsafe_allow_html=True)
            st.markdown("""
                <style>
                table {
                    width: 100%;
                    border-collapse: collapse;
                }
                th, td {
                    text-align: center;
                    border: 1px solid #ddd;
                    padding: 8px;
                }
                th {
                    background-color: #f4f4f4;
                    font-weight: bold;
                }
                tr:nth-child(even) {
                    background-color: #f9f9f9;
                }
                tr:hover {
                    background-color: #f1f1f1;
                }
                </style>
            """, unsafe_allow_html=True)

            html_table = filtered_df.to_html(classes="table", header=True, index=True)

            # Streamlit에서 HTML로 표시
            st.markdown(html_table, unsafe_allow_html=True)
    else:
        st.warning("변화량을 계산할 이전 데이터가 없습니다.")

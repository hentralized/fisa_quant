import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def get_triangle(df, name) : # 상승 하강 삼각형 
    if pd.isna(df.loc['PER(배)'].iloc[-1]) :
        st.markdown(
        '<span style="background-color:#E2E2E2; font-size:80%;">최근 데이터가 존재하지 않습니다</span>',
        unsafe_allow_html=True
        )
        recent_value = df.loc[name].iloc[-2]   
        prevent_value = df.loc[name].iloc[-3]
    else :
        recent_value = df.loc[name].iloc[-1]   
        prevent_value = df.loc[name].iloc[-2]
        
    if recent_value >= prevent_value :
        answer = '🔼'
    else :
        answer = '🔽'
    return recent_value, answer 


def show_bar_chart(df, columns_to_draw, title ="재무제표 주요 항목 비교") : 
    df = df.loc[columns_to_draw]
    df.columns = [col[1] for col in df.columns]
    df_transpose = df.T
    
    fig = go.Figure()
    df_transpose.index = pd.to_datetime(df_transpose.index).strftime('%Y/%m')
    
    custom_colors = ["#001C91","#5E9EA0", "#67E8C3","#3B5998", "#6BC59C"]

    fig = go.Figure()

    for idx, row_label in enumerate(df.index):
        if row_label in df_transpose.columns:
            fig.add_trace(go.Bar(
                x=df_transpose.index, # 기간 
                y=df_transpose[row_label],  # Data for each metric
                name=row_label,  
                marker_color=custom_colors[idx % len(custom_colors)]  # 색 지정하기 
            ))
            
    fig.update_layout(
        title=title,
        xaxis_title="기간",
        yaxis_title="금액",
        barmode="group",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        template="plotly_white"
    )

    return fig
    
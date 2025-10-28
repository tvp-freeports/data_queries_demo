import streamlit as st;st.set_page_config(layout="wide")
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import random

from src.Bubblechart import BubbleChart
from src.Constants import COLORS_SEQUENCE

def list_filter_df(df, ohchr2023, unsr_opt, dbio2024):
    if ohchr2023:
        df = df[df['List - OHCHR 2023']==1]
    if unsr_opt:
        df = df[df['List - UNSR OPT']==1]
    if dbio2024:
        df = df[df['List - DBIO24']==1]
    
    return df 

# -----------------------------------------------
st.title(f'THIS IS **THE** TITLE')
st.header('This is the header')
st.subheader(f'This is the subheader')
st.write('This is a simple text snippet')
st.markdown(f'**this is a bold text**')
st.markdown(f'*this is a italic text*')
st.markdown(f'this is not a bold text')

with st.sidebar:
    st.header('Work explanation')
    st.write(":rainbow[Lorem] :green[ipsum] :blue[dolor] :red[sit] :orange[amet], consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.")

    user_type = st.sidebar.selectbox('', options=['users','pro-users','developers'])

# -----------------------------------------------

BASE_NAME = '{}.xlsx'
DATA_ROOT = './data/'
NAMES = ['MDN', 'ISP']
YEARS = [ '2023', '2024']

name     = st.selectbox('select the associated banking group you would like to analyse',options=NAMES)
year     = st.selectbox('select the year you would like to analyse',options=YEARS)

filename     = 'r{}_{}'.format(name, year)

_cols = st.columns([0.33,0.34,0.33])
with _cols[0]:
    ohchr2023    = st.checkbox('mark it if you want to analyze record in list OHCHR 2023')
with _cols[1]:
    unsr_opt     = st.checkbox('mark it if you want to analyze record in list UNSR OPT')
with _cols[2]:
    dbio2024     = st.checkbox('mark it if you want to analyze record in list DBIO 2024')

if filename:

    df = pd.read_excel(DATA_ROOT + BASE_NAME.format(filename))
    df = df.fillna(value='UNK')
    df = list_filter_df(df, ohchr2023, unsr_opt, dbio2024)
    df['year'] = [filename.split('_')[1]] * df.shape[0]

    df_bubble = df.groupby(['Sub-fund']).sum()
    
    browser_market_value = {
    'subfund': df_bubble.index.to_list(),
    'market_value': df_bubble['Market value in EUR as of June 2025'].to_list(),
    'color': COLORS_SEQUENCE[:df_bubble.shape[0]]
    }

    bubble_chart = BubbleChart(area=browser_market_value['market_value'],
                            bubble_spacing=0.1)

    bubble_chart.collapse()

    #pyplot plot
    scatter = bubble_chart.plotly_plot(browser_market_value['subfund'])
    st.plotly_chart(scatter)

    _cols = st.columns([0.75,0.25])
    subfund = st.selectbox('select the fund to analyse', options = df_bubble.index.to_list())
    compare = st.checkbox('compare with another subfund')

    df_subfund = df[df['Sub-fund'] == subfund]

    _cols = st.columns([0.5,0.5])

    with _cols[0]:
        st.subheader('Investee company legal name x Management Companies')
        pie = px.sunburst(df_subfund,path=['Management Company', 'Investee company legal name'], values = 'Market value in EUR as of June 2025')
        st.plotly_chart(pie)

    with _cols[1]:
        df_beneficiarie = df_subfund[['Investee company legal name', 'Market value in EUR as of June 2025']].groupby('Investee company legal name').sum().sort_values(by= 'Market value in EUR as of June 2025',ascending=False)
        portion = st.radio('Scoieta beneficiarie per market value',['head','tail','all'])
        if portion == 'head':
                df_beneficiarie = df_beneficiarie.head()
        if portion == 'tail':
            df_beneficiarie = df_beneficiarie.tail()
        
        hist = px.bar(df_beneficiarie, x = df_beneficiarie.index, y='Market value in EUR as of June 2025', color=df_beneficiarie.index)
        st.plotly_chart(hist)

    st.subheader('Info about the Fund and the Umbrella Fund the Sub-Fund selected belongs')
    try:
        assert len(list(set(df_subfund['Management Company']))) == 1
        assert len(list(set(df_subfund['Umbrella fund']))) == 1
    except Exception:
        st.stop('Something went wrong! There is an unconcistency in the data')
    
    fund          = list(set(df_subfund['Management Company']))[0]
    umbrella_fund = list(set(df_subfund['Umbrella fund']))[0]

    df_fund         = df[df['Management Company'] == fund]
    df_umbrellafund = df[df['Umbrella fund'] == umbrella_fund]

    st.write('The :blue[{}] subfund is parte of the {} umbrella fund which is part of {} fund'.format(subfund, umbrella_fund, fund))
    _cols = st.columns([0.33, 0.34, 0.33])
    with _cols[0]:
        pie_funds = px.sunburst(df,path=['Management Company'], values = 'Market value in EUR as of June 2025')
        st.plotly_chart(pie_funds)

    with _cols[1]:
        pie_umbfunds = px.sunburst(df_fund,path=['Umbrella fund'], values = 'Market value in EUR as of June 2025')
        st.plotly_chart(pie_umbfunds)

    with _cols[2]:
        pie_companies = px.sunburst(df_umbrellafund, path=['Investee company legal name'], values = 'Market value in EUR as of June 2025')
        st.plotly_chart(pie_companies)

    if compare:
        subfunds_to_compare = df_bubble.index.to_list()
        subfunds_to_compare.remove(subfund)

        subfund_compare = st.selectbox('select another subfund to compare it with the previous one', options = subfunds_to_compare)
        if subfund_compare:
            df_subfund_compare = df[df['Sub-fund'].isin([subfund, subfund_compare])]
            bar_compare = px.bar(df_subfund_compare, x = 'Investee company legal name', y='Market value in EUR as of June 2025', color='Sub-fund', barmode='group')
            _cols = st.columns([0.7,0.3])
            with _cols[0]:
                st.plotly_chart(bar_compare)
            with _cols[1]:
                pie_compare = px.sunburst(df_subfund_compare,path=['Sub-fund'], values = 'Market value in EUR as of June 2025')
                st.plotly_chart(pie_compare)







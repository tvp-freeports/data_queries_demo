import streamlit as st
import pandas as pd
import plotly.express as px
import random

st.title(f'THIS IS **THE** TITLE')
st.header('This is the header')
st.subheader(f'This is the subheader')
st.write('This is a simple text snippet')
st.markdown(f'**this is a bold text**')
st.markdown(f'this is not a bold text')


with st.sidebar:
    st.header('Work explanation')
    st.write(":rainbow[Lorem] :green[ipsum] :blue[dolor] :red[sit] :orange[amet], consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.")
    user_type = st.sidebar.selectbox('', options=['users','pro-users','developers'])

BASE_NAME = 'r{}.xlsx'
DATA_ROOT = './data/'
YEARS = [None, '2023', '2024']

year = st.selectbox('select the  year you would like to analyse',options=YEARS)

if year:
    df = pd.read_excel(DATA_ROOT + BASE_NAME.format(year))
    
    df = df.fillna(value='UNK')
    df['year'] = [year] * df.shape[0]

    companies_list = st.selectbox('select the companies list you would like to focus on',options=[None, 'List - OHCHR 2023','List - UNSR OPT, Francesca Albanese', 'List - DBIO24'])
    
    if companies_list:
        df = df[df[companies_list]==1]

    if user_type != 'users':
            with st.expander('drill down on the row data'):
                st.write(df)

    _cols = st.columns([0.5,0.5])

    with _cols[0]:
        st.subheader('Management Companies')
        pie = px.sunburst(df,path=['year','Management Company'], values = 'Market value in EUR as of June 2025')
        st.plotly_chart(pie)

    with _cols[1]:
        df_beneficiarie = df[['Investee company legal name', 'Market value in EUR as of June 2025']].groupby('Investee company legal name').sum().sort_values(by= 'Market value in EUR as of June 2025',ascending=False)
        portion = st.radio('Scoieta beneficiarie per market value',['head','tail','all'])
        if portion == 'head':
                df_beneficiarie = df_beneficiarie.head()
        if portion == 'tail':
            df_beneficiarie = df_beneficiarie.tail()

        hist = px.bar(df_beneficiarie, x = df_beneficiarie.index, y='Market value in EUR as of June 2025', color=df_beneficiarie.index)
        st.plotly_chart(hist)

    company    = st.selectbox('select the Company you would like to analyse', options=set(df['Management Company']))
    df_company = df[df['Management Company']==company]
    umbrella   = st.selectbox('select the Fund you would like to analyse', options=set(df_company['Umbrella fund']))
    df_umbrella   = df[df['Umbrella fund']==umbrella]
    hist = px.bar(df_umbrella, y = df_umbrella['Sub-fund'], x='Market value in EUR as of June 2025', color=df_umbrella['Investee company legal name'])
    st.plotly_chart(hist)
    
    st.subheader('select the Sub-Fund you would like to focous on!')
    st.write('Note that the previous filters are still active.')
    df_subfunds = df_umbrella[['Sub-fund','Market value in EUR as of June 2025']].groupby('Sub-fund').sum()
    df_subfunds['Sub-funds'] = df_subfunds.index

    _cols = st.columns([0.5,0.5])
    with _cols[0]:
        pie = px.sunburst(df_subfunds, path=['Sub-funds'], values = 'Market value in EUR as of June 2025')
        st.plotly_chart(pie)
    with _cols[1]:
        subfunds    = st.selectbox('select the Company you would like to analyse', options=set(df_umbrella['Sub-fund']))
        df_subfunds = df[df['Sub-fund']==subfunds]

        df_umb_beneficiarie = df_subfunds[['Investee company legal name', 'Market value in EUR as of June 2025']].groupby('Investee company legal name').sum().sort_values(by= 'Market value in EUR as of June 2025',ascending=False)
        hist = px.bar(df_umb_beneficiarie, x = df_umb_beneficiarie.index, y='Market value in EUR as of June 2025', color=df_umb_beneficiarie.index)
        st.plotly_chart(hist)

    with st.expander('Check the dataset filtered by Managment Company: {} and Umbrella Fund: {} and Sub Funds: {}'.format(company, umbrella, subfunds)):
        st.write(df_umb_beneficiarie)



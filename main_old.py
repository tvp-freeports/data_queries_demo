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

BASE_NAME = '{}_output_st.csv'
DATA_ROOT = './data/'
INVESTORS = [None, 'ANIMA','EURIZON', 'AMUNDI']

investor = st.selectbox('select the investment found you would like to analyse',options=INVESTORS)

df1 = pd.read_excel('/workspaces/emm-dev-kb/notebooks/founds-investiments/data/r2024.xlsx')
st.write(df1)

df2 = pd.read_excel('/workspaces/emm-dev-kb/notebooks/founds-investiments/data/r2023.xlsx')
st.write(df2)

if investor:
    df = pd.read_csv(DATA_ROOT + BASE_NAME.format(investor.lower()))
    

    df = df.dropna()
    df['found'] = [investor] * df.shape[0]
    df['size']  =  [x*10 for x in df['% net asset']]
    df['asset_manager'] = [x.split()[0][-2:] for x in df['subfund']]
    del df['Unnamed: 0']

    
    if user_type != 'users':
            with st.expander('drill down on the row data'):
                st.write(df)

    _cols = st.columns([0.5,0.5])

    with _cols[0]:
        pie = px.sunburst(df,path=['found','company'], values = 'fair value')
        st.plotly_chart(pie)
    with _cols[1]:
        metadata = st.selectbox('select the feature you want to be represente', options=['subfund'])
        pie = px.sunburst(df,path=['found', metadata], values = 'fair value')
        st.plotly_chart(pie)

    scatter = px.scatter(df, x="company", y="% net asset", color="subfund",size='size', hover_data=['found'])
    st.plotly_chart(scatter)

    company = st.selectbox('select the copany you want to analyse',options=[None] + list(set(df.company)))

    if company:
        df_company = df[df['company']==company]

        if st.checkbox('exclude outliers'):
            thr = int(st.text_input('input threshold'))
            if thr:
                df_company = df_company[df_company['fair value'] < thr]

        company_scatter = px.scatter(df_company,x='fair value',y='fair value', color='subfund', size ='size', hover_data=['found','% net asset'])
        st.plotly_chart(company_scatter)
import streamlit as st
st.set_page_config(layout="wide")
import pandas as pd
import plotly.express as px

from src.Bubblechart import BubbleChart
from src.Constants import COLORS_SEQUENCE
from src.utils import list_filter_df

# --- Disclaimer gate ---------------------------------------------------------

if "disclaimer_accepted" not in st.session_state:
    st.session_state.disclaimer_accepted = False

if not st.session_state.disclaimer_accepted:
    st.markdown(
        """
        <h3 style='color:red;'>⚠️ Disclaimer</h3>
        <p style='font-size:16px;'>
        The content displayed on the Portlight platform is currently provided <strong>for demonstration purposes only.</strong><br><br>
        <strong> None of the data </strong> outlined should be interpreted as a correct representation of the monetary exposures
        towards companies linked to human rights and environmental violations, nor the names of any company or relationship between companies should be taken as accurate.
        <br><br>
        By proceeding, <strong> the reader acknowledges </strong> that the following content represent a mere prototype, useful only as a sketch for future work with no  accuracy of the data outlined at the present stage.
        </p>
        """,
        unsafe_allow_html=True
    )

    if st.button("Proceed to Portlight"):
        st.session_state.disclaimer_accepted = True
        st.rerun()

    st.stop()

# --- Sidebar --------------------------------------------

with st.sidebar:
    st.header('Work explanation')
    st.write(
        ":rainbow[Lorem] :green[ipsum] :blue[dolor] :red[sit] :orange[amet], consectetur adipiscing elit, "
        "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud "
        "exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit "
        "in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, "
        "sunt in culpa qui officia deserunt mollit anim id est laborum."
    )
    user_type = st.sidebar.selectbox('', options=['users', 'pro-users', 'developers'])

# --- Portlight -------------------------------------------------------------------------- 

st.title("Portlight")

st.markdown(
    "<h3 style='font-size:22px;'>Freeports' data portal on controversial investments.</h3>",
    unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)

# --- Category selection "portal" ---
if "fi_selected" not in st.session_state:
    st.session_state.fi_selected = None

if st.session_state.fi_selected is None:
    st.markdown(
        "<p style='font-size:17px; font-style:italic;'>Select the category of financial institution to assess:</p>",
        unsafe_allow_html=True
    )
    fi = st.radio('', options=['— Select —', 'Investment funds', 'Banking groups'], index=0)
    if fi != '— Select —':
        st.session_state.fi_selected = fi
        st.rerun()
else:
    fi = st.session_state.fi_selected

# --- first 'opening' --------------------------------------------

if fi == 'Investment funds':

    # Load the unified dataset
    df = pd.read_csv('./data/portlight_data.csv')

    # User selections

#     year = st.selectbox(
#         'Select the publication year',
#         options=sorted(df['Publication date'].astype(str).str.split('.').str[0].unique())
# )

#     # Filter by selected year
#     df = df[df['Publication date'].str.startswith(year)]

    # Header and inline Go-back button
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.markdown("<h2 style='margin-top:0; margin-bottom:1.2rem;'> EU funds' portfolios</h2>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)  # vertical align adjustment
        if st.button("← Go back", key="back_button", use_container_width=True):
            st.session_state.fi_selected = None
            st.rerun()

    st.markdown(
        "Mark to discover the funds' holdings in companies identified as controversial according to one or more of the following lists:",
        unsafe_allow_html=True
    )

    # Filter options
    _cols = st.columns([1, 1, 1, 1, 1, 1])
    
    with _cols[0]:
        ohchr2023 = st.checkbox('OHCHR 2023')
    with _cols[1]:
        unsr_opt = st.checkbox('UNSR OPT')
    with _cols[2]:
        dbio2024 = st.checkbox('DBIO 2024')
    with _cols[3]:
        ohchr2025 = st.checkbox('OHCHR 2025')
    with _cols[4]:
        traseearth = st.checkbox('TRASE.EARTH')
    with _cols[5]:
        testonly = st.checkbox('TEST ONLY')    

    # Clean and filter
    df = df.fillna(value='UNK')
    df = list_filter_df(df, ohchr2023, unsr_opt, dbio2024, ohchr2025, traseearth, testonly)

    # Bubble chart setup
    df_bubble = df.groupby(['Sub-fund']).sum(numeric_only=True)
    browser_market_value = {
        'subfund': df_bubble.index.to_list(),
        'market_value': df_bubble['Market value in EUR'].to_list(),
        'color': COLORS_SEQUENCE[:df_bubble.shape[0]]
    }

    bubble_chart = BubbleChart(area=browser_market_value['market_value'], bubble_spacing=0.1)
    bubble_chart.collapse()

    scatter = bubble_chart.plotly_plot(browser_market_value['subfund'])
    st.plotly_chart(scatter)

    st.markdown(
        "<p style='margin-top:-60px; font-size:14px; font-style:italic; color:gray;'>"
        "Each bubble represents the sum of the fund's investments"
        " towards companies from the selected list"
        "</p>",
        unsafe_allow_html=True
    )

    st.header('Individual fund analysis')

    # Subfund selection
    _cols = st.columns([0.75, 0.25])

    st.markdown(
        "<p style='margin-bottom:-60px;'>Select the fund of interest</p>",
        unsafe_allow_html=True
    )
    subfund = st.selectbox('', options=df_bubble.index.to_list())

    compare = st.checkbox('Compare with another fund\'s investments')

    df_subfund = df[df['Sub-fund'] == subfund]

    if not compare:
        _cols = st.columns([0.5, 0.5])

        with _cols[1]:
            pie = px.sunburst(df_subfund, path=['Sub-fund', 'Investee company legal name'],
                              values='Market value')
            st.plotly_chart(pie)

        with _cols[0]:
            df_beneficiarie = (
                df_subfund[['Investee company legal name', 'Market value']]
                .groupby('Investee company legal name').sum()
                .sort_values(by='Market value', ascending=False)
            )

            portion = st.radio('Investee company by market value', ['head', 'tail', 'all'])
            if portion == 'head':
                df_beneficiarie = df_beneficiarie.head()
            elif portion == 'tail':
                df_beneficiarie = df_beneficiarie.tail()

            hist = px.bar(df_beneficiarie, x=df_beneficiarie.index,
                          y='Market value', color=df_beneficiarie.index)
            st.plotly_chart(hist)
    else:
        subfunds_to_compare = df_bubble.index.to_list()
        subfunds_to_compare.remove(subfund)
        subfund_compare = st.selectbox('', options=subfunds_to_compare)

        if subfund_compare:
            df_subfund_compare = df[df['Sub-fund'].isin([subfund, subfund_compare])]
            bar_compare = px.bar(df_subfund_compare, x='Investee company legal name',
                                 y='Market value', color='Sub-fund', barmode='group')
            _cols = st.columns([0.7, 0.3])
            with _cols[0]:
                st.plotly_chart(bar_compare)
            with _cols[1]:
                pie_compare = px.sunburst(df_subfund_compare, path=['Sub-fund'],
                                          values='Market value')
                st.plotly_chart(pie_compare)
    
    # -----------------------------------------------
    # Data download for pro-users
    if user_type == 'pro-users':
        with st.expander('Download the raw data'):
            universe = st.checkbox('Mark if you want to download the universe-level data for the selected list')
            if universe:
                st.write(df)

            interest = st.checkbox('Mark if you want to download the fund analysis data')
            if interest:
                st.write(f'Dataframe concerns for the :violet[{subfund}] fund')
                st.write(df_subfund)
                if compare:
                    st.write(f'Dataframe concerns for the :red[{subfund_compare}] fund')
                    st.write(df_subfund_compare)

elif fi == 'Banking groups':
    st.write("Page under development")

    # Go back button (new feature)
    if st.button("← Go back"):
        st.session_state.fi_selected = None
        st.rerun()

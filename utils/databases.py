import streamlit as st
import pandas as pd


from utils.create_session import create_session
from utils.database_view import show_database_page
from utils.create_database import initialize_create_database
from utils.update_query_param import update_query_params
from utils.format_date import format_date

def initialize_session_state():
    if "databases" not in st.session_state:
        st.session_state.databases = []
    if "schemas" not in st.session_state:
        st.session_state.schemas = []
    if "tables" not in st.session_state:
        st.session_state.tables = []
    if "selected_db" not in st.session_state:
        st.session_state.selected_db = None
    if "selected_schema" not in st.session_state:
        st.session_state.selected_schema = None
    if "selected_table" not in st.session_state:
        st.session_state.selected_table = None
    if "session" not in st.session_state:
        st.session_state.session = None

def initial_layout():
    if "session" not in st.session_state:
        st.balloons()
        st.session_state.session = create_session()

    if "session" in st.session_state:
        st.session_state.is_session_connected = True
        
    # #breadcrumbs
    # st.write(f"`Database` > `{st.session_state.selected_db and st.session_state.selected_db}` > `{st.session_state.selected_schema and st.session_state.selected_schema}` > `{st.session_state.selected_table and st.session_state.selected_table}`")
    
def fetch_database_details():

    st.title("Database")
    st.subheader("Explore your databases here")
    _, right_col = st.columns([9, 3])
    with right_col:
        if st.button("Create Database", type='primary', icon=":material/add:"):
            initialize_create_database()
    try:
        results = st.session_state.session.sql("SHOW DATABASES;").collect()
        st.session_state.databases = results
        st.markdown("### 📂 Available Databases:")
       
        col1, col2, col3 = st.columns([4, 3, 3])
        with col1:
            st.caption("##### ***NAME***")
        with col2:
            st.caption("##### ***OWNER***")
        with col3:
            st.caption("##### ***CREATED ON***")

        index = 0
        for row in st.session_state.databases:
            index = index + 1
            with col1:
                if st.button(f"**{row.name}**", type = "tertiary", key = f"db_{row.name}"):
                    update_query_params(db=row.name)
                    st.rerun()
            with col2:
                st.button(f"{row.owner}", type = "tertiary", key = f"owner_{index}",  disabled = True)
                # st.markdown(f"{row.owner}")
            with col3:
                st.button(f"{format_date(row.created_on)}", type = "tertiary",  key = f"created_{index}", disabled = True)

    except Exception as e:
        st.error(f"Error fetching Databases: {e}")

def initialize_databases():
    initialize_session_state()
    initial_layout()
    query_params = st.query_params
    st.session_state.selected_db = query_params.get("db")

    if st.session_state.selected_db:
        show_database_page()
    else:
        fetch_database_details()
 
import streamlit as st

from utils.create_session import create_session
from utils.database_view import show_database_page
from utils.create_database import initialize_create_database
from utils.update_query_param import update_query_params

def initialize_session_state():
    if "database_names" not in st.session_state:
        st.session_state.database_names = []
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
    #breadcrumbs
    st.write(f"`Database` > `{st.session_state.selected_db and st.session_state.selected_db}` > `{st.session_state.selected_schema and st.session_state.selected_schema}` > `{st.session_state.selected_table and st.session_state.selected_table}`")

    

def fetch_database_details():

    st.title("Database")
    st.subheader("Explore your databases here")
    _, right_col = st.columns([8, 2])
    with right_col:
        if st.button("Create Database +", type='primary'):
            initialize_create_database()
    try:
        results = st.session_state.session.sql("SHOW DATABASES;").collect()
        st.session_state.database_names = [row.as_dict()["name"] for row in results]
        st.markdown("### 📂 Available Databases:")
        for name in st.session_state.database_names:
            if st.button(f"{name}"):
                update_query_params(db=name)
                st.rerun()
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
 
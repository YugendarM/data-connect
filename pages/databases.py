import streamlit as st

from utils.create_session import create_session
from utils.database_view import show_database_page
from utils.create_database import initialize_create_database

def initialize_session_state():
    if "database_names" not in st.session_state:
        st.session_state.database_names = []
    if "selected_db" not in st.session_state:
        st.session_state.selected_db = None
    if "selected_schema" not in st.session_state:
        st.session_state.selected_schema = None

def initial_layout():
    if "session" not in st.session_state:
        st.session_state.session = create_session()

    

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
            st.markdown(f'<a href="?db={name}" target="_self">{name}</a>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error fetching Databases: {e}")

def main():
    initialize_session_state()
    initial_layout()
    query_params = st.query_params
    st.session_state.selected_db = query_params.get("db")

    if st.session_state.selected_db:
        show_database_page()
    else:
        fetch_database_details()
    st.write(st.session_state.session)

if __name__ == "__main__":
    st.set_page_config(page_title = "Database", layout = "wide")
    main()
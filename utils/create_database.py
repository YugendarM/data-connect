import streamlit as st
import pandas as pd

def initialize_session_state():
    if "new_database_name" not in st.session_state:
        st.session_state.new_database_name = None

def create_database():
    if not st.session_state.get("session"):
        st.error("Session not found")
        return

    try:
        result = st.session_state.session.sql(
            f"CREATE DATABASE {st.session_state.new_database_name};"
        ).collect()
        st.success(f"Database '{st.session_state.new_database_name}' created successfully")

    except Exception as e:
        error_message = str(e)
        if "already exists" in error_message:
            st.error("A database with this name already exists.")
        elif "invalid identifier" in error_message:
            st.error("Invalid database name. Please use only valid characters.")
        elif "permission denied" in error_message:
            st.error("You do not have permission to create a database.")
        else:
            st.error(f"Unexpected error: {error_message}")
    finally:
        st.rerun()

@st.dialog("Create New Database") 
def initialize_create_database():
    initialize_session_state()
    new_database_name = st.text_input(label = "Name", key = "new_database_name", value = st.session_state.new_database_name)  
    
    if st.button("Create"):
        create_database()
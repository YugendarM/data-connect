import streamlit as st

def initialize_session_state():
    if "new_schema_name" not in st.session_state:
        st.session_state.new_schema_name = ""

@st.dialog("Create New Schema")
def initialize_create_schema():
    initialize_session_state()

    new_schema_name = st.text_input("Schema Name", key="new_schema_name")
    
    if st.button("Create"):
        if not new_schema_name:
            st.warning("Please enter a schema name.")
            return
        create_schema(new_schema_name)

def create_schema(schema_name):
    if not st.session_state.get("session"):
        st.error("Session not found.")
        return

    try:
        session = st.session_state.session
        db = st.session_state.selected_db

        session.sql(f"USE DATABASE {db}").collect()

        result = session.sql(f"CREATE OR ALTER SCHEMA {schema_name}").collect()
        
        st.toast(f"Schema `{schema_name}` created successfully in database `{db}`.")
        st.rerun()

    except Exception as e:
        error_message = str(e).lower()
        if "already exists" in error_message:
            st.error("A schema with this name already exists.")
        elif "invalid identifier" in error_message:
            st.error("Invalid schema name. Please use only valid characters.")
        elif "permission denied" in error_message:
            st.error("You do not have permission to create a schema.")
        else:
            st.error(f"Unexpected error: {error_message}")

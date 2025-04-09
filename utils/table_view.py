import streamlit as st

def fetch_table_contents():
    try:
        results = st.session_state.session.sql(f"SELECT * FROM {st.session_state.selected_db}.{st.session_state.selected_schema}.{st.session_state.selected_table} LIMIT 30;").collect()
        if len(results) == 0:
            st.write("No records found in this table")
        st.write(results)
       
    except Exception as e:
        st.error(f"Error fetching Table contents: {e}")

def show_table_page():
    if st.session_state.selected_table is not None:
        st.title(f"Table: `{st.session_state.selected_table}`")
        st.write(f"Welcome to `{st.session_state.selected_table}` dashboard.")

        fetch_table_contents()

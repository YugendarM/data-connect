import streamlit as st

from utils.create_table import initialize_create_table
from utils.table_view import show_table_page
from utils.update_query_param import update_query_params
from utils.format_date import format_date

def fetch_table_details():
    if st.session_state.selected_schema is not None:
        st.title(f"📁 Schema: `{st.session_state.selected_schema}`")
        st.write(f"Welcome to `{st.session_state.selected_schema}` dashboard.")
    _, right_col = st.columns([8, 2])
    with right_col:
        if st.button("Create Table +", type='primary'):
            initialize_create_table()
    try:
        results = st.session_state.session.sql(f"SHOW TABLES IN SCHEMA {st.session_state.selected_db}.{st.session_state.selected_schema}").collect()
        st.session_state.tables = results
        st.markdown(f"###  Available Tables in {st.session_state.selected_db} . {st.session_state.selected_schema}")

        if len(st.session_state.tables) == 0:
            st.write("No tables found on this schemaa")

        else:
            col1, col2, col3 = st.columns([4, 3, 2])
            with col1:
                st.caption("##### ***NAME***")
            with col2:
                st.caption("##### ***OWNER***")
            with col3:
                st.caption("##### ***CREATED ON***")

            index = 0
            for row in st.session_state.tables:
                index = index + 1
                with col1:
                    if st.button(f"**{row.name}**", type = "tertiary", key = f"db_{row.name}"):
                        update_query_params(table=row.name)
                        st.rerun()
                with col2:
                    st.button(f"{row.owner}", type = "tertiary", key = f"owner_{index}",  disabled = True)
                    # st.markdown(f"{row.owner}")
                with col3:
                    st.button(f"{format_date(row.created_on)}", type = "tertiary",  key = f"created_{index}", disabled = True)
    except Exception as e:
        st.error(f"Error fetching Tables: {e}")

def show_schema_page():

    query_params = st.query_params
    st.session_state.selected_table = query_params.get("table")

    if st.session_state.selected_table:
        show_table_page()
    else:
        fetch_table_details()


    





import streamlit as st

from utils.create_table import initialize_create_table
from utils.table_view import show_table_page
from utils.update_query_param import update_query_params

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
        st.session_state.table_names = [row.as_dict()["name"] for row in results]
        st.markdown(f"###  Available Tables in {st.session_state.selected_db} . {st.session_state.selected_schema}")

        if len(st.session_state.table_names) == 0:
            st.write("No tables found on this schemaa")
        for name in st.session_state.table_names:
            if st.button(f"{name}"):
                update_query_params(table=name)
                st.rerun()
    except Exception as e:
        st.error(f"Error fetching Tables: {e}")

def show_schema_page():

    query_params = st.query_params
    st.session_state.selected_table = query_params.get("table")

    if st.session_state.selected_table:
        show_table_page()
    else:
        fetch_table_details()


    





# import streamlit as st
# from utils.create_table import initialize_create_table
# from utils.table_view import show_table_page

# def fetch_table_details(set_query_params):
#     st.title(f"📁 Schema: `{st.session_state.selected_schema}`")
#     st.write(f"Welcome to `{st.session_state.selected_schema}` dashboard.")

#     _, right_col = st.columns([8, 2])
#     with right_col:
#         if st.button("Create Table +", type='primary'):
#             initialize_create_table()

#     try:
#         results = st.session_state.session.sql(
#             f"SHOW TABLES IN SCHEMA {st.session_state.selected_db}.{st.session_state.selected_schema}"
#         ).collect()
#         st.session_state.table_names = [row.as_dict()["name"] for row in results]

#         st.markdown(f"### 📄 Tables in `{st.session_state.selected_db}.{st.session_state.selected_schema}`")
#         if not st.session_state.table_names:
#             st.info("No tables found in this schema.")
#         for name in st.session_state.table_names:
#             st.markdown(
#                 f'<a href="?db={st.session_state.selected_db}&schema={st.session_state.selected_schema}&table={name}" target="_self">{name}</a>',
#                 unsafe_allow_html=True
#             )
#     except Exception as e:
#         st.error(f"Error fetching Tables: {e}")

# def show_schema_page(set_query_params):
#     query_params = st.query_params
#     st.session_state.selected_table = query_params.get("table")

#     if st.session_state.selected_table:
#         show_table_page(set_query_params)
#     else:
#         fetch_table_details(set_query_params)

#     if st.button("⬅ Back to schemas list"):
#         set_query_params(schema=None, table=None)
#         st.rerun()

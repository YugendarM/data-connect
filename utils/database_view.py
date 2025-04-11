import streamlit as st

from utils.schema_view import show_schema_page
from utils.create_schema import initialize_create_schema
from utils.update_query_param import update_query_params

def fetch_schema_details():
    st.title(f"📁 Database: `{st.session_state.selected_db}`")
    st.write(f"Welcome to `{st.session_state.selected_db}` dashboard.")
    _, right_col = st.columns([8, 2])
    with right_col:
        if st.button("Create Schema +", type='primary'):
            initialize_create_schema()
    
    try:
        results = st.session_state.session.sql(f"SHOW SCHEMAS IN DATABASE {st.session_state.selected_db}").collect()
        st.session_state.schema_names = [row.as_dict()["name"] for row in results]
        st.markdown(f"## 📂 Available Schemas in : `{st.session_state.selected_db}`")
        for name in st.session_state.schema_names:
            if st.button(f"{name}"):
                update_query_params(schema=name)
                st.rerun()
    except Exception as e:
        st.error(f"Error fetching Schemas: {e}")

def show_database_page():

    query_params = st.query_params
    st.session_state.selected_schema = query_params.get("schema")

    if st.session_state.selected_schema:
        show_schema_page()
    else:
        fetch_schema_details()

    if st.button("⬅ Back to database list"):
        st.query_params.clear()
        st.rerun()






# import streamlit as st
# from utils.schema_view import show_schema_page
# from utils.create_schema import initialize_create_schema

# def fetch_schema_details(set_query_params):
#     st.title(f"📁 Database: `{st.session_state.selected_db}`")
#     st.write(f"Welcome to `{st.session_state.selected_db}` dashboard.")

#     _, right_col = st.columns([8, 2])
#     with right_col:
#         if st.button("Create Schema +", type='primary'):
#             initialize_create_schema()

#     try:
#         results = st.session_state.session.sql(
#             f"SHOW SCHEMAS IN DATABASE {st.session_state.selected_db}"
#         ).collect()
#         st.session_state.schema_names = [row.as_dict()["name"] for row in results]
#         st.markdown(f"## 📂 Schemas in `{st.session_state.selected_db}`")
#         for name in st.session_state.schema_names:
#             st.markdown(
#                 f'<a href="?db={st.session_state.selected_db}&schema={name}" target="_self">{name}</a>',
#                 unsafe_allow_html=True
#             )
#     except Exception as e:
#         st.error(f"Error fetching Schemas: {e}")

# def show_database_page(set_query_params):
#     query_params = st.query_params
#     st.session_state.selected_schema = query_params.get("schema")

#     if st.session_state.selected_schema:
#         show_schema_page(set_query_params)
#     else:
#         fetch_schema_details(set_query_params)

#     if st.button("⬅ Back to database list"):
#         set_query_params(db=None, schema=None, table=None)
#         st.rerun()

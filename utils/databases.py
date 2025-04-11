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
    if "selected_table" not in st.session_state:
        st.session_state.selected_table = None
    if "session" not in st.session_state:
        st.session_state.session = None

def initial_layout(snowflake_user, snowflake_password, snowflake_account):
    if "session" not in st.session_state:
        st.balloons()
        st.session_state.session = create_session(snowflake_user, snowflake_password, snowflake_account)

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
            st.markdown(f'<a href="?db={name}" target="_self">{name}</a>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error fetching Databases: {e}")

def initialize_databases(snowflake_user, snowflake_password, snowflake_account):
    initialize_session_state()
    initial_layout(snowflake_user, snowflake_password, snowflake_account)
    query_params = st.query_params
    st.session_state.selected_db = query_params.get("db")

    if st.session_state.selected_db:
        show_database_page()
    else:
        fetch_database_details()
    # st.write(st.session_state.session)

# if __name__ == "__main__":
#     st.set_page_config(page_title = "Database", layout = "wide")
#     main()




# import streamlit as st
# from utils.create_session import create_session
# from utils.database_view import show_database_page
# from utils.create_database import initialize_create_database

# def initialize_session_state():
#     if "database_names" not in st.session_state:
#         st.session_state.database_names = []
#     if "selected_db" not in st.session_state:
#         st.session_state.selected_db = None
#     if "selected_schema" not in st.session_state:
#         st.session_state.selected_schema = None
#     if "selected_table" not in st.session_state:
#         st.session_state.selected_table = None

# def set_query_params(**kwargs):
#     new_params = dict(st.query_params)
#     for key, value in kwargs.items():
#         if value is None and key in new_params:
#             del new_params[key]
#         elif value is not None:
#             new_params[key] = value
#     st.query_params = new_params

# def show_breadcrumb():
#     breadcrumb = ["`Database`"]
#     db = st.session_state.selected_db
#     schema = st.session_state.selected_schema
#     table = st.session_state.selected_table

#     if db:
#         breadcrumb.append(f'<a href="?db={db}">{db}</a>')
#     if db and schema:
#         breadcrumb.append(f'<a href="?db={db}&schema={schema}">{schema}</a>')
#     if db and schema and table:
#         breadcrumb.append(f'<a href="?db={db}&schema={schema}&table={table}">{table}</a>')

#     st.markdown(" > ".join(breadcrumb), unsafe_allow_html=True)

# def fetch_database_details():
#     st.title("Database")
#     st.subheader("Explore your databases here")

#     _, right_col = st.columns([8, 2])
#     with right_col:
#         if st.button("Create Database +", type='primary'):
#             initialize_create_database()

#     try:
#         results = st.session_state.session.sql("SHOW DATABASES;").collect()
#         st.session_state.database_names = [row.as_dict()["name"] for row in results]
#         st.markdown("### 📂 Available Databases:")
#         for name in st.session_state.database_names:
#             st.markdown(f'<a href="?db={name}" target="_self">{name}</a>', unsafe_allow_html=True)
#     except Exception as e:
#         st.error(f"Error fetching Databases: {e}")

# def main():
#     st.set_page_config(page_title="Database", layout="wide")

#     initialize_session_state()

#     # Load selected items from query params
#     params = st.query_params
#     st.session_state.selected_db = params.get("db")
#     st.session_state.selected_schema = params.get("schema")
#     st.session_state.selected_table = params.get("table")

#     if "session" not in st.session_state:
#         st.session_state.session = create_session()

#     show_breadcrumb()

#     if st.session_state.selected_db:
#         show_database_page(set_query_params)
#     else:
#         fetch_database_details()

# if __name__ == "__main__":
#     main()

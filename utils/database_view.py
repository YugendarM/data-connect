import streamlit as st

from utils.schema_view import show_schema_page
from utils.create_schema import initialize_create_schema
from utils.update_query_param import update_query_params
from utils.format_date import format_date

def fetch_schema_details():
    st.title(f"📁 Database: `{st.session_state.selected_db}`")
    st.write(f"Welcome to `{st.session_state.selected_db}` dashboard.")
    _, right_col = st.columns([9, 3])
    with right_col:
        if st.button("Create Schema", type='primary', icon=":material/add:"):
            initialize_create_schema()
    
    try:
        results = st.session_state.session.sql(f"SHOW SCHEMAS IN DATABASE {st.session_state.selected_db}").collect()
        st.session_state.schemas = results
        st.markdown(f"## 📂 Available Schemas in : `{st.session_state.selected_db}`")
        # for row in st.session_state.schemas:
        #     if st.button(f"{row.name}"):
        #         update_query_params(schema=row.name)
        #         st.rerun()

        col1, col2, col3 = st.columns([4, 3, 3])
        with col1:
            st.caption("##### ***NAME***")
        with col2:
            st.caption("##### ***OWNER***")
        with col3:
            st.caption("##### ***CREATED ON***")

        index = 0
        for row in st.session_state.schemas:
            index = index + 1
            with col1:
                if st.button(f"**{row.name}**", type = "tertiary", key = f"db_{row.name}"):
                    update_query_params(schema=row.name)
                    st.rerun()
            with col2:
                st.button(f"{row.owner}", type = "tertiary", key = f"owner_{index}",  disabled = True)
                # st.markdown(f"{row.owner}")
            with col3:
                st.button(f"{format_date(row.created_on)}", type = "tertiary",  key = f"created_{index}", disabled = True)
    except Exception as e:
        st.error(f"Error fetching Schemas: {e}")

def show_database_page():

    query_params = st.query_params
    st.session_state.selected_schema = query_params.get("schema")

    if st.session_state.selected_schema:
        show_schema_page()
    else:
        fetch_schema_details()

    st.write("")  # Blank line
    st.empty()    # Placeholder
    st.text("")   # Also creates a little gap
    if st.button("Back to database list", icon=":material/arrow_back:"):
        st.query_params.clear()
        st.rerun()





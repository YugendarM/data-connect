import streamlit as st
from utils.upload_file_data import upload_data_to_table
from utils.edit_table import edit_table_structure

def fetch_table_description():
    table_description = st.session_state.session.sql(
        f"DESC TABLE {st.session_state.selected_db}.{st.session_state.selected_schema}.{st.session_state.selected_table};"
    ).collect()

    simplified_description = []
    for row in table_description:
        constraints = []
        if row["null?"] == "N":
            constraints.append("NOT NULL")
        if row["primary key"] == "Y":
            constraints.append("PRIMARY KEY")
        if row["unique key"] == "Y":
            constraints.append("UNIQUE")
        if row["check"]:
            constraints.append(f"CHECK ({row['check']})")
        if row["expression"]:
            constraints.append(f"EXPRESSION ({row['expression']})")
        if row["default"]:
            constraints.append(f"DEFAULT {row['default']}")
        if row["comment"]:
            constraints.append(f"COMMENT '{row['comment']}'")
        if row["policy name"]:
            constraints.append(f"POLICY: {row['policy name']}")
        if row["privacy domain"]:
            constraints.append(f"PRIVACY DOMAIN: {row['privacy domain']}")

        simplified_description.append({
            "Column Name": row["name"],
            "Data Type": row["type"],
            "Constraints": ", ".join(constraints) if constraints else "None"
        })

    with st.expander("📋 Table Description"):
        st.dataframe(simplified_description, use_container_width=True)

    st.markdown("---")


    return [[row["name"] for row in table_description], simplified_description]  # Return column names


def fetch_table_contents():
    try:
        [column_names, table_description] = fetch_table_description()

        if st.button("Edit Table", type = "primary"):
            edit_table_structure(table_description)

        if st.button("Add Record +", type="secondary"):
            print()  

        upload_data_to_table()

        st.markdown("---")

        st.markdown("### 🔍 Search & Filter")
        
        _, search_col, limit_col = st.columns([3, 4, 3])

        with search_col:
            search_query = st.text_input(label="Search all columns..", placeholder="Type to Search")

        with limit_col:
            result_limit = st.number_input(
                label="Number of rows to fetch", min_value=1, value=30, step=1
            )

        _, search_col = st.columns([7, 1])
        with search_col:
            search_triggered = st.button("Search", type="primary")

        where_clause = ""
        if search_triggered and search_query.strip():
            like_statements = [f'"{col}" ILIKE \'%{search_query.strip()}%\'' for col in column_names]
            where_clause = f"WHERE {' OR '.join(like_statements)}"

        query = f"""
            SELECT * 
            FROM {st.session_state.selected_db}.{st.session_state.selected_schema}.{st.session_state.selected_table}
            {where_clause}
            LIMIT {result_limit};
        """

        results = st.session_state.session.sql(query).collect()

        if not results:
            st.warning("No records found.")
        else:
            st.dataframe(results, use_container_width=True)

    except Exception as e:
        st.error(f"Error fetching Table contents: {e}")


def show_table_page():
    if st.session_state.selected_table is not None:
        st.title(f"Table: `{st.session_state.selected_table}`")
        st.write(f"Welcome to `{st.session_state.selected_table}` dashboard.")
        fetch_table_contents()

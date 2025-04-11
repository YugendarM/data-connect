import streamlit as st

from utils.upload_file_data import upload_data_to_table

def fetch_table_description():
    # Fetch full table description
    table_description = st.session_state.session.sql(
        f"DESC TABLE {st.session_state.selected_db}.{st.session_state.selected_schema}.{st.session_state.selected_table};"
    ).collect()

    # Format constraints per column
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

    # Display the simplified table
    with st.expander("📋 Table Description"):
        st.dataframe(simplified_description, use_container_width=True)




def fetch_table_contents():
    try:
        fetch_table_description()

        results = st.session_state.session.sql(f"SELECT * FROM {st.session_state.selected_db}.{st.session_state.selected_schema}.{st.session_state.selected_table} LIMIT 30;").collect()
        # _, col1, col2 = st.columns([10, 2, 2])
        # with col1:
        #     if st.button("Add Record +", type = "primary"):
        #         print()
        # with col2:
        #     if st.button("Import from file ", type = "primary"):
        #         upload_data_to_table()

        if st.button("Add Record +", type = "primary"):
            print()

        # if st.button("Import from file ", type = "primary"):
        upload_data_to_table()

        if len(results) == 0:
            st.write("No records found in this table")
        else:            
            st.write(results)
       
    except Exception as e:
        st.error(f"Error fetching Table contents: {e}")

def show_table_page():
    if st.session_state.selected_table is not None:
        st.title(f"Table: `{st.session_state.selected_table}`")
        st.write(f"Welcome to `{st.session_state.selected_table}` dashboard.")

        fetch_table_contents()






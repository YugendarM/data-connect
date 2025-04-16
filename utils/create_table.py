import streamlit as st

def initialize_session_state():
    if "new_table_name" not in st.session_state:
        st.session_state.new_table_name = ""
    if "columns" not in st.session_state:
        st.session_state.columns = []

@st.dialog("Create New Table")
def initialize_create_table():
    initialize_session_state()

    new_table_name = st.text_input("Table Name", key="new_table_name", value=st.session_state.new_table_name)

    _, right_col = st.columns([4, 2])
    with right_col:
        if st.button("Add Column", icon=":material/add:"):
            st.session_state.columns.append({
                "name": "",
                "type": "VARCHAR(25)",
                "constraints": []
            })

    updated_columns = []
    for index, column in enumerate(st.session_state.columns):
        col1, col2, col3 = st.columns(3)

        with col1:
            field_name = st.text_input(
                f"Field name {index + 1}",
                value=column.get("name", ""),
                key=f"field_name_{index}"
            )

        with col2:
            field_type = st.selectbox(
                f"Field type {index + 1}",
                options=["VARCHAR(5)", "VARCHAR(10)", "VARCHAR(25)", "VARCHAR(50)", "VARCHAR(100)", "VARCHAR(255)", "INTEGER", "FLOAT", "BOOLEAN", "DATE"],
                index=["VARCHAR(5)", "VARCHAR(10)", "VARCHAR(25)", "VARCHAR(50)", "VARCHAR(100)", "VARCHAR(255)", "INTEGER", "FLOAT", "BOOLEAN", "DATE"].index(column.get("type", "VARCHAR(25)")),
                key=f"field_type_{index}"
            )

        with col3:
            constraints = st.multiselect(
                f"Constraints {index + 1}",
                options=["PRIMARY KEY", "UNIQUE", "NOT NULL", "AUTO INCREMENT", "FOREIGN KEY"],
                default=column.get("constraints", []),
                key=f"constraints_{index}"
            )

        # todo: have to check if all the constraints are added properly

        updated_columns.append({
            "name": field_name.strip(),
            "type": field_type,
            "constraints": constraints
        })

    st.session_state.columns = updated_columns
    
    if st.button("Create Table", icon=":material/add:"):
        if not st.session_state.new_table_name.strip():
            st.error("Table name is required!")
        elif len(st.session_state.columns) == 0:
            st.error("Add at least one column before creating a table.")
        elif not all(col["name"] for col in st.session_state.columns):
            st.error("All fields must have names.")
        else:
            st.success("Captured Columns:")
            create_table(st.session_state.new_table_name, st.session_state.columns)
            st.write(st.session_state.columns)

def create_table(table_name, columns):
    if not st.session_state.get("session"):
        st.error("Session not found.")
        return

    try:
        session = st.session_state.session
        db = st.session_state.selected_db
        schema = st.session_state.selected_schema 

        session.sql(f"USE DATABASE {db}").collect()
        session.sql(f"USE SCHEMA {schema}").collect()

        column_defs = []
        for col in columns:
            constraints = " ".join(col.get("constraints", []))
            column_defs.append(f"{col['name']} {col['type']} {constraints}".strip())

        columns_sql = ",\n  ".join(column_defs)
        query = f"CREATE TABLE {schema}.{table_name} (\n  {columns_sql}\n);"

        result = session.sql(query).collect()
        
        st.toast(f"✅ Table `{table_name}` created successfully in `{db}.{schema}`.")
        st.code(query, language="sql")
        st.rerun()

    except Exception as e:
        error_message = str(e).lower()
        if "already exists" in error_message:
            st.error("A table with this name already exists.")
        elif "invalid identifier" in error_message:
            st.error("Invalid table name. Please use only valid characters.")
        elif "permission denied" in error_message:
            st.error("You do not have permission to create a table.")
        else:
            st.error(f"Unexpected error: {error_message}")

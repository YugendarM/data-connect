import streamlit as st

@st.dialog("Edit Table")
def edit_table_structure(table_description):
    st.markdown("### Edit Table Structure")

    if "new_columns" not in st.session_state:
        st.session_state.new_columns = []

    column_name_changes = {}
    column_type_changes = {}
    column_constraints = {}

    existing_column_names = [col["Column Name"] for col in table_description]

    for i, column in enumerate(table_description):
        col_name = column["Column Name"]
        col_type = column["Data Type"]

        col_type = "INTEGER" if col_type == "NUMBER(38,0)" else col_type

        valid_column_types = ["VARCHAR(5)", "VARCHAR(10)", "VARCHAR(25)", "VARCHAR(50)", "VARCHAR(100)", "VARCHAR(255)", "INTEGER", "FLOAT", "BOOLEAN", "DATE"]

        if col_type not in valid_column_types:
            col_type = "VARCHAR(255)"

        new_name = st.text_input(f"Column Name: {col_name}", value=col_name, key=f"edit_name_{i}")

        new_type = st.selectbox(
            f"Column Type for {col_name}",
            valid_column_types,
            index=valid_column_types.index(col_type),
            key=f"edit_type_{i}"
        )

        current_constraints = column.get("constraints", [])
        constraints = st.multiselect(
            f"Constraints for {col_name}",
            options=["NOT NULL", "UNIQUE", "DEFAULT", "PRIMARY KEY", "AUTO INCREMENT", "FOREIGN KEY"],
            default=current_constraints,
            key=f"constraints_{i}"
        )

        column_constraints[col_name] = constraints

        if new_name != col_name:
            column_name_changes[col_name] = new_name

        if new_type != col_type:
            column_type_changes[col_name] = new_type

    st.divider()
    st.subheader("Add New Columns")

    for i, col in enumerate(st.session_state.new_columns):
        col_name = st.text_input(f"New Column Name {i+1}", value=col.get("name", ""), key=f"new_name_{i}")
        col_type = st.selectbox(
            f"New Column Type {i+1}",
            valid_column_types,
            index=valid_column_types.index(col.get("type", "VARCHAR(50)")),
            key=f"new_type_{i}"
        )
        constraints = st.multiselect(
            "Constraints",
            options=["NOT NULL", "UNIQUE", "DEFAULT", "PRIMARY KEY", "AUTO INCREMENT", "FOREIGN KEY"],
            default=col.get("constraints", []),
            key=f"new_constraints_{i}"
        )

        st.session_state.new_columns[i] = {
            "name": col_name,
            "type": col_type,
            "constraints": constraints
        }

    if st.button("Add New Column"):
        st.session_state.new_columns.append({
            "name": "",
            "type": "VARCHAR(50)",
            "constraints": []
        })

    st.divider()
    column_to_delete = st.selectbox("Mark Column to Delete", existing_column_names)
    if st.button("Mark for Deletion"):
        if "columns_to_delete" not in st.session_state:
            st.session_state.columns_to_delete = set()
        st.session_state.columns_to_delete.add(column_to_delete)
        st.success(f"Marked {column_to_delete} for deletion.")

    st.divider()

    # --- SAVE CHANGES ---
    if st.button("Save Changes", type="primary"):
        db = st.session_state.selected_db
        schema = st.session_state.selected_schema
        table = st.session_state.selected_table
        full_table = f"{db}.{schema}.{table}"

        queries = []

        for col in st.session_state.new_columns:
            if not col["name"] or not col["type"]:
                st.error("All new columns must have name and type.")
                return

        for col_name, new_type in column_type_changes.items():
            queries.append(f'ALTER TABLE {full_table} ALTER COLUMN {col_name} SET DATA TYPE {new_type};')

        for col_name, constraints in column_constraints.items():
            for constraint in constraints:
                if constraint == "NOT NULL":
                    queries.append(f'ALTER TABLE {full_table} ALTER COLUMN {col_name} SET NOT NULL;')
                elif constraint == "UNIQUE":
                    queries.append(f'ALTER TABLE {full_table} ADD CONSTRAINT {col_name}_unique UNIQUE ({col_name});')
                elif constraint == "DEFAULT":
                    default_value = "DEFAULT_VALUE"  
                    queries.append(f'ALTER TABLE {full_table} ALTER COLUMN {col_name} SET DEFAULT {default_value};')

        # RENAME COLUMNS LAST
        for old, new in column_name_changes.items():
            queries.append(f'ALTER TABLE {full_table} RENAME COLUMN {old} TO {new};')

        # DELETE COLUMNS
        if "columns_to_delete" in st.session_state:
            for col in st.session_state.columns_to_delete:
                queries.append(f'ALTER TABLE {full_table} DROP COLUMN {col};')
            del st.session_state.columns_to_delete

        # ADD NEW COLUMNS
        for col in st.session_state.new_columns:
            col_def = f"{col['name']} {col['type']}"
            for constraint in col["constraints"]:
                if constraint == "NOT NULL":
                    col_def += " NOT NULL"
                elif constraint == "DEFAULT":
                    col_def += f" DEFAULT {col['default']}"  # Add appropriate default value logic
            queries.append(f"ALTER TABLE {full_table} ADD COLUMN {col_def};")

            for constraint in col["constraints"]:
                if constraint == "UNIQUE":
                    queries.append(f'ALTER TABLE {full_table} ADD CONSTRAINT {col["name"]}_unique UNIQUE ({col["name"]});')

        # EXECUTE ALL QUERIES
        try:
            for q in queries:
                query_result = st.session_state.session.sql(q).collect()
                st.write(query_result)
                st.write(f"✅ `{q}`")
            st.success("Changes saved successfully.")
            st.session_state.new_columns.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

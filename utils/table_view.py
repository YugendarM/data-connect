import streamlit as st
import pandas as pd

from utils.upload_file_data import upload_data_to_table
from utils.edit_table import edit_table_structure

def clean_value(value):
    """Cleans the value to replace None, NULL, or empty string with an empty space."""
    if value is None or value == "NULL" or value == "":
        return ""
    return value


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

        # Buttons for edit & add
    

    st.markdown("---")
    return [[row["name"] for row in table_description], simplified_description]


@st.dialog("Add new record:")
def add_record(column_names):
    new_record = {}
    for col in column_names:
        new_record[col] = st.text_input(col, key=f"add_{col}")

    if st.button("Submit Record"):
        try:
            # Ensure empty fields are handled as empty string (not NULL)
            cols = ", ".join(f'"{col}"' for col in new_record)
            # vals = ", ".join(f'"{new_record[col] if new_record[col] != '' else ''}"' for col in new_record.values())
            st.balloons()
            st.write(vals)

            insert_query = f"""
                INSERT INTO {st.session_state.selected_db}.{st.session_state.selected_schema}.{st.session_state.selected_table}
                ({cols}) VALUES ({vals});
            """
            st.write(insert_query)
            st.session_state.session.sql(insert_query).collect()
            st.success("Record added successfully.")
            st.rerun()
        except Exception as e:
            st.error(f"Error inserting record: {e}")


def fetch_table_contents():
    try:
        column_names, table_description = fetch_table_description()

        if st.button("🛠️ Edit Table Structure", type="secondary"):
            edit_table_structure(table_description)


        upload_data_to_table()

        # _, col1 = st.columns([8, 2])
        # with col1:
        #     if st.button("➕ Add Record", type='primary'):
        #         add_record(column_names)

        st.markdown("---")

        st.markdown("### 🔍 Search & Filter")

        _, search_col, limit_col = st.columns([3, 4, 3])
        with search_col:
            search_query = st.text_input("Search all columns..", placeholder="Type to Search")
        with limit_col:
            result_limit = st.number_input("Number of rows to fetch", min_value=1, value=30, step=1)

        _, search_btn_col = st.columns([15, 2])
        with search_btn_col:
            search_triggered = st.button("Search", type="primary")
        
        # Search logic
        where_clause = ""
        if search_triggered and search_query.strip():
            like_statements = [f'"{col}" ILIKE \'%{search_query.strip()}%\'' for col in column_names]
            where_clause = f"WHERE {' OR '.join(like_statements)}"

        query = f"""
            SELECT * FROM {st.session_state.selected_db}.{st.session_state.selected_schema}.{st.session_state.selected_table}
            {where_clause}
            LIMIT {result_limit};
        """

        raw_results = st.session_state.session.sql(query).collect()

        if not raw_results:
            st.warning("No records found.")
            return

        original_data = [
            {k: clean_value(v) for k, v in row.asDict().items()}
            for row in raw_results
        ]

        st.markdown("### 📄 Table Overview")

        edited_data = st.data_editor(
            original_data,
            use_container_width=True,
            num_rows="dynamic",
            key="editable_table"
        )

        # def convert_for_download(df):
        #     return df.to_csv().encode("utf-8")

        # Detect changes
        changes = []
        for old_row, new_row in zip(original_data, edited_data):
            if old_row != new_row:
                changes.append((old_row, new_row))

        df = pd.DataFrame(edited_data)

        csv = df.to_csv().encode("utf-8")

        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="data.csv",
            mime="text/csv",
            icon=":material/download:",
        )

        if changes and st.button("💾 Save Changes", type="primary"):
            for old_row, new_row in changes:
                # Constructing the SET clause by ensuring empty strings for empty fields
                set_clause = ", ".join(
                    [f'"{col}" = \'{new_row[col] if new_row[col] != "" else ""}\'' for col in column_names]
                )
                # Using ID only in the WHERE clause to match the record
                where_clause = f'"ID" = \'{old_row["ID"]}\''

                update_query = f"""
                    UPDATE {st.session_state.selected_db}.{st.session_state.selected_schema}.{st.session_state.selected_table}
                    SET {set_clause}
                    WHERE {where_clause};
                """
                try:
                    st.session_state.session.sql(update_query).collect()
                except Exception as e:
                    st.error(f"Error updating row: {e}")
            st.success("Changes saved successfully.")
            st.rerun()

    except Exception as e:
        st.error(f"Error fetching Table contents: {e}")


def show_table_page():
    if st.session_state.selected_table is not None:
        st.title(f"Table: `{st.session_state.selected_table}`")
        st.write(f"Welcome to `{st.session_state.selected_table}` dashboard.")
        fetch_table_contents()

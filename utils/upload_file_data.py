import os
import shutil
import tempfile
import traceback
import pandas as pd
import streamlit as st
from io import StringIO, BytesIO
import gc
from snowflake.connector.pandas_tools import write_pandas

def upload_data_to_table():
    if not all([
        st.session_state.get("selected_db"),
        st.session_state.get("selected_schema"),
        st.session_state.get("selected_table")
    ]):
        st.warning("Please select a database, schema, and table first.")
        return

    uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv"], key="file_uploader")

    if uploaded_file and (
        "uploaded_filename" not in st.session_state or
        st.session_state.uploaded_filename != uploaded_file.name
    ):
        try:
            file_bytes = uploaded_file.read()
            if uploaded_file.name.endswith(".csv"):
                decoded = file_bytes.decode("utf-8")
                df = pd.read_csv(StringIO(decoded))
            else:
                df = pd.read_excel(BytesIO(file_bytes))

            st.session_state.uploaded_df = df
            st.session_state.uploaded_filename = uploaded_file.name
            st.session_state.file_ready = True
            st.session_state.upload_validation_passed = False

        except PermissionError:
            st.error("❌ File permission error. The file may be in use by another process.")
            st.code(traceback.format_exc())
            return
        except UnicodeDecodeError:
            st.error("❌ Unable to decode the file. Make sure it's a UTF-8 encoded CSV.")
            st.code(traceback.format_exc())
            return
        except Exception as e:
            st.error(f"❌ Error reading file: {e}")
            st.code(traceback.format_exc())
            return

    if st.session_state.get("file_ready") and "uploaded_df" in st.session_state:
        df = st.session_state.uploaded_df

        st.subheader("Preview of Uploaded Data")
        st.dataframe(df.head())

        if not st.session_state.get("upload_validation_passed", False):
            session = st.session_state.session
            full_table = f"{st.session_state.selected_db}.{st.session_state.selected_schema}.{st.session_state.selected_table}"

            try:
                desc_result = session.sql(f"DESC TABLE {full_table}").collect()
                table_schema = {row['name'].lower(): row['type'].upper() for row in desc_result}

                df.columns = df.columns.str.strip().str.lower()

                if set(df.columns) != set(table_schema.keys()):
                    st.error(f"❌ Column mismatch!\n\nExpected: {list(table_schema.keys())}\n\nFound: {list(df.columns)}")
                    return

                pandas_type_map = {
                    "NUMBER": ["int64", "float64"],
                    "FLOAT": ["float64"],
                    "VARCHAR": ["object", "string"],
                    "BOOLEAN": ["bool"],
                    "DATE": ["datetime64[ns]"],
                    "TIMESTAMP": ["datetime64[ns]"],
                }

                mismatches = []
                for col, expected_type in table_schema.items():
                    expected_family = next((key for key in pandas_type_map if key in expected_type), None)
                    if expected_family:
                        if df[col].dtype.name not in pandas_type_map[expected_family]:
                            mismatches.append(f"{col}: expected {expected_family}, got {df[col].dtype.name}")
                    else:
                        mismatches.append(f"{col}: unknown expected type `{expected_type}`")

                if mismatches:
                    st.error("❌ Datatype mismatches:\n" + "\n".join(mismatches))
                    return

                st.success("✅ File is compatible! Ready to upload.")
                st.session_state.upload_validation_passed = True

            except Exception as e:
                st.error(f"❌ Error validating file: {e}")
                st.code(traceback.format_exc())
                return

        #todo: have to handle errors when uploading (error while query is processing)
        if st.session_state.get("upload_validation_passed"):
            if st.button("Upload to Table"):
                    try:
                        df = st.session_state.uploaded_df
                        session = st.session_state.session

                        st.info("📤 Uploading data to Snowflake...")

                        # Normalize column names (strip + lowercase)
                        df.columns = df.columns.str.strip().str.lower()

                        # Get existing column names from target Snowflake table
                        table_ref = session.table(f"{st.session_state.selected_db}.{st.session_state.selected_schema}.{st.session_state.selected_table}")
                        existing_columns = [col.name.lower() for col in table_ref.schema]

                        uploaded_columns = df.columns.tolist()

                        # Check column match before uploading
                        if sorted(existing_columns) != sorted(uploaded_columns):
                            st.error("⚠️ Column names in uploaded file do not match the target table.")
                            st.code(f"Expected: {sorted(existing_columns)}\nUploaded: {sorted(uploaded_columns)}")
                            st.stop()

                        # ✅ Main fix: quote_identifiers=False
                        write_result = session.write_pandas(
                            df,
                            table_name=st.session_state.selected_table,
                            database=st.session_state.selected_db,
                            schema=st.session_state.selected_schema,
                            auto_create_table=False,
                            overwrite=False,
                            quote_identifiers=False  # <== fixes the "invalid identifier" issue
                        )

                        st.success(f"✅ Data uploaded successfully!")
                        # res = session.sql(
                        #     f"SELECT COUNT(*) FROM {st.session_state.selected_db}.{st.session_state.selected_schema}.{st.session_state.selected_table}"
                        # ).collect()
                        # st.write(f"📊 Total rows in table now: {res[0][0]}")
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Upload failed: {e}")
                        st.code(traceback.format_exc())


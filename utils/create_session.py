import streamlit as st
from snowflake.snowpark import Session
import os

# @st.cache_resource
# def create_session():
#     return Session.builder.configs(st.secrets.snowflake).create()


@st.cache_resource
def create_session():
    connection_parameters = {
        "user": os.getenv("SNOWFLAKE_USER"),
        "password": os.getenv("SNOWFLAKE_PASSWORD"),
        "account": os.getenv("SNOWFLAKE_ACCOUNT")
    }
    return Session.builder.configs(connection_parameters).create()
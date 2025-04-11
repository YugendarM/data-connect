import streamlit as st
from snowflake.snowpark import Session

@st.cache_resource
def create_session(snowflake_user, snowflake_password, snowflake_account):
    connection_parameters = {
        "user": snowflake_user,
        "password": snowflake_password,
        "account": snowflake_account
    }
    return Session.builder.configs(connection_parameters).create()
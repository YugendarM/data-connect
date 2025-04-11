import streamlit as st

def update_query_params(**kwargs):
    st.query_params.update(kwargs)
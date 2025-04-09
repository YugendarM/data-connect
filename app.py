import streamlit as st

from utils.create_session import create_session

def testing():
    if("test" not in st.session_state):
        st.session_state.test = "testing"

def initialize_session_state():
    if('session' not in st.session_state):
        st.session_state.session = ""

def initial_layout():
    st.title("Welcome to Data-Connect")
    connect_session()

def connect_session():
    st.session_state.session = create_session()
    st.success("Snowflake connected successfully")
    st.write(st.session_state.session)






def main():
    initialize_session_state()
    initial_layout()
    
    # testing()

if __name__ == "__main__":
    st.set_page_config(page_title="Data-Connect", layout="wide")
    main()





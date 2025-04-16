import streamlit as st
from utils.create_session import create_session
from utils.databases import initialize_databases

def initialize_session_state():
    defaults = {
        "session": None,
        "is_session_connected": False,
        "current_role" : None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def fetch_user_role():
    _, col1, col2, col3 = st.columns([5, 3, 5, 3])

    with col1:
        st.markdown("##### Current Role:")

    with col2:
        current_role_result = st.session_state.session.sql("SELECT CURRENT_ROLE()").collect()
        st.session_state.current_role = current_role_result[0][0]
        roles_result = st.session_state.session.sql("SHOW ROLES").collect()
        available_roles = [row['name'] for row in roles_result]
        new_role = st.selectbox("", available_roles, index=available_roles.index(st.session_state.current_role) if st.session_state.current_role in available_roles else 0, label_visibility="collapsed")


    with col3:    
        if st.button("`Change Role`"):
            try:
                st.session_state.session.sql(f"USE ROLE {new_role}").collect()
                st.toast(f"Role changed to `{new_role}` successfully.")
                st.rerun() 
            except Exception as e:
                st.error(f"Error switching role: {str(e)}")
    


def clear_session():
    st.session_state.is_session_connected = False
    st.query_params.clear()
    st.session_state.pop("session", None)
    st.rerun()

def initial_layout():
    snowflake_user = ""
    snowflake_password = ""
    snowflake_account = ""

    st.title("Welcome to Data-Connect")

    if not st.session_state.is_session_connected:
        with st.form("login_form"):
            snowflake_user = st.text_input(
                label="Username",
                placeholder="eg: 'JohnDoe3'",
                key="snowflake_user"
            )
            snowflake_password = st.text_input(
                label="Password",
                type="password",
                placeholder="eg: '*************'",
                key="snowflake_password"
            )
            snowflake_account = st.text_input(
                label="Account",
                placeholder="eg: 'deefc-23ed'",
                key="snowflake_account"
            )
            submit = st.form_submit_button("Connect")

            if submit:
                if not all([
                    snowflake_user.strip(),
                    snowflake_password.strip(),
                    snowflake_account.strip()
                ]):
                    st.error("All fields are required!")
                else:
                    try:
                        st.session_state.session = create_session(snowflake_user, snowflake_password, snowflake_account)
                        st.session_state.is_session_connected = True
                        st.success("✅ Snowflake connected successfully!")
                        st.rerun()

                    except Exception as e:
                        st.session_state.session = None
                        st.session_state.is_session_connected = False

                        error_msg = str(e).lower()

                        if "404" in error_msg or "not found" in error_msg:
                            st.error(f"❌ User not found. Please check your username and your account. {str(e)}")
                        elif "443" in error_msg or "unauthorized" in error_msg:
                            st.error("❌ Incorrect username or password.")
                        elif "account" in error_msg and "invalid" in error_msg:
                            st.error("❌ Invalid account ID.")
                        elif "timeout" in error_msg:
                            st.error("❌ Connection timed out. Please try again.")
                        else:
                            st.error(f"❌ Connection failed: {str(e)}")

    else:
        st.success("✅ You are connected to Snowflake.")
        fetch_user_role()

        initialize_databases()

        st.markdown("---")

        if st.button("Logout Session", icon=":material/logout:"):
            clear_session()

def main():
    initialize_session_state()
    initial_layout()

if __name__ == "__main__":
    st.set_page_config(page_title="Data-Connect")
    main()

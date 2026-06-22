import streamlit as st
from database import register_user, login_user, init_db

def show_auth():
    init_db()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "auth_username" not in st.session_state:
        st.session_state.auth_username = ""

    if st.session_state.logged_in:
        return True

    st.markdown("""
    <style>
    .auth-wrap {
        max-width: 420px;
        margin: 4rem auto;
    }
    .auth-title {
        font-family: Georgia, serif;
        font-size: 2.2rem;
        color: #343148;
        margin-bottom: 4px;
    }
    .auth-sub {
        color: #8B7355;
        font-style: italic;
        font-size: 14px;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<p class="auth-title">✨ Aura AI</p>', unsafe_allow_html=True)
        st.markdown('<p class="auth-sub">Your personal growth companion</p>', unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔑 Login", "🌸 Register"])

        with tab1:
            st.markdown("### Welcome back")
            username = st.text_input("Username", key="login_user", placeholder="Enter username")
            password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter password")
            if st.button("Login ✨", key="login_btn", use_container_width=True):
                if not username or not password:
                    st.error("Please fill in both fields!")
                elif login_user(username, password):
                    st.session_state.logged_in = True
                    st.session_state.auth_username = username.lower()
                    st.rerun()
                else:
                    st.error("Wrong username or password!")

        with tab2:
            st.markdown("### Create your account")
            new_user = st.text_input("Username", key="reg_user", placeholder="Choose a username")
            new_pass = st.text_input("Password", type="password", key="reg_pass", placeholder="Choose a password")
            confirm = st.text_input("Confirm password", type="password", key="reg_confirm", placeholder="Confirm password")
            if st.button("Create account 🌸", key="reg_btn", use_container_width=True):
                if not new_user or not new_pass:
                    st.error("Please fill in all fields!")
                elif new_pass != confirm:
                    st.error("Passwords don't match!")
                elif len(new_pass) < 4:
                    st.error("Password must be at least 4 characters!")
                elif register_user(new_user, new_pass):
                    st.success("Account created! Please login 🌸")
                else:
                    st.error("Username already taken!")

    return False
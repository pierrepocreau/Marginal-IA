import streamlit as st
from utils.db import get_supabase_client

# App branding and description
col1, col2 = st.columns([2, 1])

with col1:
    st.title("Marginal⋅IA")
    st.markdown("### Note-Taking app for physical books")
    st.markdown("""
    Capture your thoughts through voice, with structure and ease.
    """)
    st.markdown("[GitHub](https://github.com/pierrepocreau/Marginal-IA)")

with col2:
    st.write("")  # Spacer
    st.write("")

st.divider()

tab1, tab2 = st.tabs(["Sign In", "Sign Up"])

with tab1:
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Sign In")

        if submit:
            try:
                with st.spinner("Logging you in..."):
                    client = get_supabase_client()
                    response = client.auth.sign_in_with_password({"email": email, "password": password})
                    # Store BOTH user and session for proper authentication
                    st.session_state.user = response.user
                    st.session_state.session = response.session
                st.rerun()
            except Exception as e:
                st.error(f"Login failed: {e}")

with tab2:
    with st.form("signup_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        st.caption("Password must be at least 8 characters.")
        submit = st.form_submit_button("Sign Up")

        if submit:
            try:
                client = get_supabase_client()
                response = client.auth.sign_up({"email": email, "password": password})
                st.success("Account created! Please check your email to confirm.")
            except Exception as e:
                st.error(f"Sign up failed: {e}")

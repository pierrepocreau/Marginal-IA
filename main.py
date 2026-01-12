import streamlit as st

st.set_page_config(page_title="Marginal·IA", page_icon="📖")

from utils.db import get_supabase_client
from utils.sidebar import render_sidebar
import time

def should_refresh_session(session):
    """Check if the session should be refreshed based on token expiration."""
    if not session or not hasattr(session, 'expires_at'):
        return True

    # Refresh if token expires in less than 5 minutes (300 seconds)
    time_until_expiry = session.expires_at - int(time.time())
    return time_until_expiry < 300

# Validate that we have a valid session
if "session" not in st.session_state or not st.session_state.get("session"):
    # No session - clear user and redirect to login
    st.session_state.user = None
elif st.session_state.get("user"):
    # We have a session - validate and refresh if needed
    try:
        supabase = get_supabase_client()
        # Set the session on the client to use the stored JWT tokens
        supabase.auth.set_session(
            st.session_state.session.access_token,
            st.session_state.session.refresh_token
        )

        # Only refresh the session if the token is close to expiring
        if should_refresh_session(st.session_state.session):
            # Refresh the session to get fresh tokens
            refreshed_session = supabase.auth.refresh_session()

            if refreshed_session and refreshed_session.session and refreshed_session.user:
                # Update with fresh session data and tokens
                st.session_state.session = refreshed_session.session
                st.session_state.user = refreshed_session.user
            else:
                # Session refresh failed - clear and force re-login
                st.session_state.user = None
                st.session_state.session = None
    except Exception:
        # Session validation/refresh failed - clear and force re-login
        st.session_state.user = None
        st.session_state.session = None
else:
    st.session_state.user = None

# Redirect to login if no valid user
if not st.session_state.get("user"):
    pg = st.navigation([st.Page("pages/login.py", title="Login")])
    pg.run()
    st.stop()

if "library" not in st.session_state:
    st.session_state.library = []

if "recorder_key" not in st.session_state:
    st.session_state.recorder_key = 0

current_book_obj = render_sidebar()

st.session_state.current_book_obj = current_book_obj

home_page = st.Page("pages/recorder.py", title="Home")
secondary_page = st.Page("pages/books.py", title="Manage Books")
third_page = st.Page("pages/notes.py", title="View all notes")

pg = st.navigation([home_page, secondary_page, third_page])

pg.run()

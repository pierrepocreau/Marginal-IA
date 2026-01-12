import streamlit as st
from supabase import create_client
import os

def _get_supabase_config():
    """Get Supabase configuration from secrets or environment variables."""
    try:
        supabase_url = st.secrets.get("SUPABASE_URL")
        supabase_key = st.secrets.get("SUPABASE_KEY")
    except (FileNotFoundError, AttributeError):
        supabase_url = None
        supabase_key = None

    supabase_url = supabase_url or os.getenv("SUPABASE_URL")
    supabase_key = supabase_key or os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY configuration")

    return supabase_url, supabase_key

def get_supabase_client():
    """
    Get a base Supabase client for authentication operations.
    NOTE: NOT cached - each call returns a fresh instance.
    This prevents session leakage between users.
    """
    try:
        supabase_url, supabase_key = _get_supabase_config()
        return create_client(supabase_url, supabase_key)
    except Exception as e:
        st.error(f"Error getting Supabase client: {e}")
        st.stop()

def get_authenticated_client():
    """
    Get a Supabase client authenticated with the current user's session.
    This ensures RLS policies are properly enforced by using the user's JWT tokens.
    DO NOT cache this function - it needs fresh auth tokens.

    Best Practice: Use this for all data operations to ensure RLS is enforced.
    """
    try:
        supabase_url, supabase_key = _get_supabase_config()
        client = create_client(supabase_url, supabase_key)

        # CRITICAL: Set the session with JWT tokens for RLS enforcement
        if st.session_state.get("session"):
            client.auth.set_session(
                st.session_state.session.access_token,
                st.session_state.session.refresh_token
            )
        elif st.session_state.get("user"):
            # User exists but no session - this shouldn't happen, force re-login
            st.session_state.user = None
            st.rerun()

        return client
    except Exception as e:
        st.error(f"Error getting authenticated client: {e}")
        st.stop()
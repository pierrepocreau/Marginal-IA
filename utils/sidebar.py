import streamlit as st
from structures.book import Book
from dataclasses import asdict
from utils.db import get_authenticated_client
from utils.isbn import lookup_isbn, is_valid_isbn

@st.cache_data(show_spinner=False)
def get_user_books(user_id: str):
    """
    Gets the books for the current user (cached per user_id).
    CRITICAL: Parameter name MUST NOT start with underscore - Streamlit ignores
    underscore-prefixed params in cache keys, causing cache collision between users!
    """
    if not user_id:
        return []

    try:
        # CRITICAL: Get a fresh authenticated client for THIS user
        client = get_authenticated_client()
        # CRITICAL: Always filter by user_id
        response = client.table("books").select("*").eq("user_id", user_id).execute()
        books = []
        for b in response.data:
            # Nettoyage des champs qui ne sont pas dans la dataclass Book
            if "user_id" in b: del b["user_id"]
            if "created_at" in b: del b["created_at"]
            books.append(Book(**b))
        return books
    except Exception:
        # Silently return empty list if not authenticated yet
        return []


def clear_books_cache():
    """Clears the books cache after mutations."""
    get_user_books.clear()

def update_selection():
    """Callback: Syncs the widget value to the permanent state."""
    selection = st.session_state.sidebar_selection
    if selection and selection != "➕ Add new book":
        st.session_state.active_book_title = selection

def render_sidebar():
    """Renders the common sidebar elements and returns the selected book."""

    if "active_book_title" not in st.session_state:
        st.session_state.active_book_title = None

    # SECURITY: Always pass user_id to prevent data leaks
    user_id = st.session_state.get("user").id if st.session_state.get("user") else None
    st.session_state.library = get_user_books(user_id) if user_id else []
    current_book_obj = None

    with st.sidebar:

        # --- Book Selector ---

        book_titles = [b.title for b in st.session_state.library]

        pre_selected_index = 0
        if st.session_state.active_book_title in book_titles:
            pre_selected_index = book_titles.index(st.session_state.active_book_title)

        col1, col2 = st.columns([0.75, 0.25])

        with col1:
            selected_title_str = st.selectbox(
                "Current book",
                book_titles,
                index=pre_selected_index,
                placeholder="Choose a book...",
                key="sidebar_selection",
                on_change=update_selection)

        with col2:
            st.write("")
            st.write("")
            if st.button("➕"):
                add_book_dialog()

        if selected_title_str:
            current_book_obj = next((b for b in st.session_state.library if b.title == selected_title_str), None)

            if current_book_obj:
                st.caption(f"Author: {current_book_obj.author}")

        st.divider()

        # --- Sign Out Button ---

        if st.button("Sign Out"):
            try:
                get_authenticated_client().auth.sign_out()
            except Exception:
                pass
            st.session_state.user = None
            st.session_state.session = None
            st.rerun()

        return current_book_obj

@st.dialog("Add new book")
def add_book_dialog():
    tab_manual, tab_isbn = st.tabs(["Manual", "ISBN Lookup"])

    with tab_isbn:
        with st.form("isbn_lookup_form"):
            isbn_input = st.text_input("Enter ISBN", placeholder="978-3-16-148410-0")

            if st.form_submit_button("Look up"):
                if not isbn_input:
                    st.error("Please enter an ISBN")
                elif not is_valid_isbn(isbn_input):
                    st.error("Invalid ISBN format")
                else:
                    _lookup_and_save_book(isbn_input)

    with tab_manual:
        with st.form("add_book_form"):
            title = st.text_input("Title")
            author = st.text_input("Author")

            if st.form_submit_button("Add"):
                _save_book(title, author)


def _lookup_and_save_book(isbn: str):
    """Look up ISBN and automatically save the book if found."""
    with st.spinner("Looking up book..."):
        book_info = lookup_isbn(isbn)

    if book_info:
        if book_info.cover_url:
            st.image(book_info.cover_url, width=100)
        st.success(f"Found: {book_info.title} by {book_info.author}")
        _save_book(book_info.title, book_info.author)
    else:
        st.error("Book not found. Try the Manual tab to enter details.")


def _save_book(title: str, author: str):
    """Save a book to the database."""
    if not title or not title.strip() or not author or not author.strip():
        st.error("Title and author are required")
        return

    try:
        new_book = Book(title=title.strip(), author=author.strip())
        book_dict = asdict(new_book)
        book_dict["user_id"] = st.session_state.user.id

        client = get_authenticated_client()
        client.table("books").insert(book_dict).execute()
        clear_books_cache()

        st.session_state.library.append(new_book)
        st.session_state.active_book_title = new_book.title

        st.success(f"Saved {title}")
        st.rerun()
    except Exception as e:
        st.error(f"Failed to save book: {e}")
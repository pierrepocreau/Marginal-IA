import streamlit as st
from utils.db import get_authenticated_client
from utils.sidebar import clear_books_cache
from structures.book import Book

st.set_page_config(page_title="Manage Books")
st.title("Manage Books")

@st.dialog("Edit Book")
def edit_book_dialog(book):
    with st.form("edit_book_form"):
        new_title = st.text_input("Title", value=book.title)
        new_author = st.text_input("Author", value=book.author)

        if st.form_submit_button("Save Changes"):
            try:
                client = get_authenticated_client()
                client.table("books").update({
                    "title": new_title,
                    "author": new_author
                }).eq("id", book.id).execute()
                clear_books_cache()

                st.success("Updated!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

user_id = st.session_state.user.id
client = get_authenticated_client()

try:
    response_books = client.table("books").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    books_data = response_books.data
except Exception as e:
    st.error(f"Error fetching books: {e}")
    st.stop()

try:
    response_notes = client.table("notes").select("book_id").eq("user_id", user_id).execute()
    all_notes = response_notes.data
except Exception as e:
    st.error(f"Error fetching note stats: {e}")
    all_notes = []

note_counts = {}
for note in all_notes:
    bid = note.get("book_id")
    if bid:
        note_counts[bid] = note_counts.get(bid, 0) + 1

library = []
for b in books_data:
    b_clean = b.copy()
    if "user_id" in b_clean: del b_clean["user_id"]
    if "created_at" in b_clean: del b_clean["created_at"]
    
    library.append(Book(**b_clean))

st.session_state.library = library

# --- 5. Display Book List ---
if not library:
    st.info("No books yet.")
else:
    for book in library:
        with st.container(border=True):
            c1, c2, c3 = st.columns([5, 2, 2])
            
            with c1:
                if st.button(f"📖 {book.title}", key=f"nav_{book.id}", help="Click to view notes"):
                    st.session_state.active_book_title = book.title
                    st.switch_page("pages/notes.py")
                
                st.caption(f"By {book.author}")
            
            with c2:
                count = note_counts.get(book.id, 0)
                st.write(f"{count} notes")

            with c3:
                col_edit, col_del = st.columns(2)
                with col_edit:
                    if st.button("Edit", key=f"edit_{book.id}", help="Edit details"):
                        edit_book_dialog(book)
                
                with col_del:
                    if st.button("🗑️", key=f"del_{book.id}", help="Delete book"):
                        try:
                            client.table("notes").delete().eq("book_id", book.id).execute()
                            client.table("books").delete().eq("id", book.id).execute()
                            clear_books_cache()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Delete failed: {e}")
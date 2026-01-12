import streamlit as st
from utils.db import get_authenticated_client
from structures.note import Note
from utils.export import generate_obsidian_export, generate_csv_export

st.set_page_config(page_title="Manage Notes")

# --- EDIT DIALOG ---
@st.dialog("Edit Note")
def edit_note_dialog(note):
    with st.form("edit_note_form"):
        new_quote = st.text_area("Quote", value=note.quote if note.quote else "")
        new_comment = st.text_area("Your Comment", value=note.comment if note.comment else "")
        new_page = st.number_input("Page Number", value=note.page_number if note.page_number else 0)

        new_content = st.text_area("Transcript/Content", value=note.content if note.content else "", height=150)

        if st.form_submit_button("Update Note"):
            try:
                client = get_authenticated_client()
                updates = {
                    "quote": new_quote,
                    "comment": new_comment,
                    "page_number": new_page if new_page > 0 else None,
                    "content": new_content
                }
                client.table("notes").update(updates).eq("id", note.id).execute()
                st.success("Note updated!")
                st.rerun()
            except Exception as e:
                st.error(f"Update failed: {e}")

# --- EXPORT DIALOG ---
@st.dialog("Export to Obsidian")
def export_dialog():
    all_notes = st.session_state.notes
    library = st.session_state.get("library", [])

    if not all_notes:
        st.warning("No notes to export")
        return

    # Build book options: only books that have notes
    books_with_notes = set(n.book_id for n in all_notes if n.book_id)
    available_books = [b for b in library if b.id in books_with_notes]

    # Create options list
    book_options = ["All books"] + [b.title for b in available_books]

    selected = st.selectbox("Select what to export", book_options)

    # Determine notes to export
    if selected == "All books":
        notes_to_export = all_notes
        filename = "marginal-ia-export.zip"
    else:
        selected_book = next((b for b in available_books if b.title == selected), None)
        if selected_book:
            notes_to_export = [n for n in all_notes if n.book_id == selected_book.id]
            filename = f"{selected_book.title}.zip"
        else:
            notes_to_export = []
            filename = "export.zip"

    # Show count
    st.caption(f"{len(notes_to_export)} notes will be exported")

    if notes_to_export:
        st.divider()

        # Format selection
        export_format = st.radio(
            "Format",
            ["Obsidian (Markdown)", "CSV (Notion, Excel)"],
            horizontal=True
        )

        if export_format == "Obsidian (Markdown)":
            zip_data = generate_obsidian_export(library, notes_to_export)
            st.download_button(
                label=" Download ZIP",
                data=zip_data,
                file_name=filename,
                mime="application/zip",
                use_container_width=True
            )
        else:
            csv_data = generate_csv_export(library, notes_to_export)
            csv_filename = filename.replace(".zip", ".csv")
            st.download_button(
                label=" Download CSV",
                data=csv_data,
                file_name=csv_filename,
                mime="text/csv",
                use_container_width=True
            )

# --- MAIN APP ---
col_title, col_export = st.columns([8, 2])
with col_title:
    st.title("My Notes")

user_id = st.session_state.user.id
client = get_authenticated_client()

try:
    response = client.table("notes").select("*").eq("user_id", user_id).execute()
    notes = [Note(**{k: v for k, v in n.items() if k not in ["user_id", "created_at"]}) for n in response.data]
    st.session_state.notes = notes
except Exception as e:
    st.error(f"Error fetching notes: {e}")
    st.session_state.notes = []
filtered_notes = st.session_state.notes
if st.session_state.current_book_obj:
    filtered_notes = [n for n in st.session_state.notes if n.book_id == st.session_state.current_book_obj.id]
    if not filtered_notes:
        st.info(f"No notes found for '{st.session_state.current_book_obj.title}'")

# --- EXPORT BUTTON (in header) ---
with col_export:
    st.write("")  # Spacing to align with title
    if st.session_state.notes and st.session_state.get("library"):
        if st.button(" Export", help="Export notes to Obsidian"):
            export_dialog()

# --- DISPLAY LOOP ---
for note in reversed(filtered_notes):
    
    # Get book title for the header (in case we are viewing "All Notes")
    book_title = next((b.title for b in st.session_state.library if b.id == note.book_id), "Unknown Book")

    with st.container(border=True):
        # --- Header ---
        c1, c2 = st.columns([8, 1])
        with c1: 
            st.caption(f"📖 {book_title}")
        with c2: 
            if note.page_number: st.caption(f"Page {note.page_number}")
        
        # --- Content ---
        if note.quote: 
            st.markdown(f"> *\"{note.quote}\"*")
        
        if note.comment: 
            st.write(f"**Note:** {note.comment}")
        elif note.content: 
            st.write(note.content)
        
        if note.tags: 
            st.caption(" • ".join([f"#{t}" for t in note.tags]))

        # --- Footer (Confidence | Actions) ---
        f1, f2 = st.columns([8, 2])
        
        with f1:
            score = getattr(note, "confidence_score", 1.0) or 1.0
            color = "green" if score > 0.8 else "orange"
            st.markdown(f"<span style='color:{color};'>●</span> Confidence: {int(score*100)}%", unsafe_allow_html=True)
        
        with f2:
            b_edit, b_del = st.columns(2)
            
            with b_edit:
                if st.button("Edit", key=f"edit_note_{note.id}", help="Edit Note"):
                    edit_note_dialog(note)

            with b_del:
                if st.button("🗑️", key=f"del_note_{note.id}", help="Delete Note"):
                    try:
                        client.table("notes").delete().eq("id", note.id).execute()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Delete failed: {e}")
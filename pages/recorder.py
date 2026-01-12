import streamlit as st
from dataclasses import asdict
from openai import OpenAI
from audiorecorder import audiorecorder
import io
import os
from structures.note import Note
from utils.parser import parse_note_content
from utils.db import get_authenticated_client

current_book = st.session_state.get("current_book_obj", None)


@st.cache_resource
def get_openai_client():
    """Returns cached OpenAI client instance."""
    try:
        api_key = st.secrets.get("OpenAI_key")
    except (FileNotFoundError, AttributeError):
        api_key = None

    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Missing OpenAI API key configuration")
    return OpenAI(api_key=api_key)

@st.cache_resource
def get_groq_client():
    try:
        api_key = st.secrets.get("GROQ_API_KEY")
    except (FileNotFoundError, AttributeError):
        api_key = None

    api_key = api_key or os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Missing Groq API key configuration")
    return OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1"
    )

st.title("Marginal·IA")
st.caption("Seamless Voice-to-Note")

st.divider()

current_book = st.session_state.get("current_book_obj", None)

audio = audiorecorder("🎙️ Start recording", "⏹️ Stop recording", key=f"recorder_{st.session_state.recorder_key}")
st.caption("Page # · Quote · Tags · Comment")


if len(audio) > 0:
    # Capture audio and increment key immediately to reset widget state
    audio_data = audio
    st.session_state.recorder_key += 1

    with st.container():
        st.write("")

        with st.status("Transcribing...", expanded=True) as status:
            try:
                # Initialize clients only when needed
                groq_client = get_groq_client()

                audio_buffer = io.BytesIO()
                audio_data.export(audio_buffer, format="wav")
                audio_buffer.name = "audio.wav"

                # Auto-detect language (supports mixed languages)
                transcript = groq_client.audio.transcriptions.create(
                    model="whisper-large-v3-turbo",
                    file=audio_buffer,
                )

                status.update(label="Parsing structure...", state="running")
                parsed_data = parse_note_content(transcript.text, groq_client)

                if not parsed_data:
                    status.update(label="Parsing failed", state="error", expanded=True)
                    st.error("Failed to parse the note structure. Please try again.")
                else:
                    if current_book:
                        new_note = Note(content=transcript.text, book_id=current_book.id, **parsed_data)
                    else:
                        new_note = Note(content=transcript.text, **parsed_data)

                    note_dict = asdict(new_note)
                    note_dict["user_id"] = st.session_state.user.id

                    supabase_client = get_authenticated_client()
                    supabase_client.table("notes").insert(note_dict).execute()

                    if "notes" not in st.session_state:
                        st.session_state.notes = []
                    st.session_state.notes.append(new_note)

                    status.update(label="Saved!", state="complete", expanded=False)

            except Exception as e:
                status.update(label="Error", state="error", expanded=True)
                st.error(f"Error: {e}")

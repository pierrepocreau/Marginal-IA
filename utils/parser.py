import json
import streamlit as st

def parse_note_content(raw_text, client):
    """
    Uses OpenAI to extract structured fields from raw voice note text.
    """

    if st.session_state.current_book_obj:
        current_book_title = st.session_state.current_book_obj.title  # e.g. "Dune"
        current_book_author = st.session_state.current_book_obj.author # e.g. "Frank Herbert"
    else:
        current_book_title = None
        current_book_author = None

    predefined_tags = ["character", "question", "remark", "quote", "summary", "idea", "connection", "critique"]
    tags_list_str = ", ".join(predefined_tags)

    system_prompt = f"""
    You are an expert editor and structuring assistant for voice notes.
    The user is currently reading the book: **"{current_book_title}" by {current_book_author}** (ignore if None).

    **IMPORTANT: Preserve the original language of the input. Do NOT translate. If the input is in French, output in French. If mixed languages, keep them as-is.**

    Your goal is to clean up the user's spoken stream of consciousness into a structured JSON note.

    ### INPUT DATA
    You will receive a raw transcript of a user speaking. They might stutter, repeat themselves, or change their mind.
    The transcript may contain phonetic misspellings of names or places specific to this book.

    ### PARSING RULES
    1. **CONTEXT & ENTITY FIXING (CRITICAL):** - Use your knowledge of the book "{current_book_title}" to CORRECT any names, places, or specific terms that were transcribed phonetically. 
    - Example: If the audio says "Cat-ness", correct it to "Katniss" (if the book is Hunger Games).

    2. **Quote vs. Comment:** - If the user says "Quote", "It says", or reads text verbatim, put that in "quote".
    - If the user says "I think", "This reminds me", or analyzes the text, put that in "comment".

    3. **Page Numbers:** - Look for "Page X", "p. X", or just numbers mentioned in context of location. Return as integer or null.

    4. **Tags:** - You MUST categorize the note using tags from this PREDEFINED LIST: [{tags_list_str}].
    - You may select 1 to 3 tags.
    - Only create a NEW tag if absolutely necessary and none of the predefined tags fit.

    5. **Cleanup:** - Fix grammar and remove filler words ("um", "uh", "like") in the comment/quote, but keep the meaning.

    ### EXAMPLES

    **Input:** "Okay on page 42 uh wait no page 45. It says that happiness is a choice. I think that's controversial because circumstances matter."
    **Output:**
    {{
    "page_number": 45,
    "quote": "Happiness is a choice.",
    "comment": "This is controversial; circumstances also play a huge role.",
    "tags": ["critique", "idea"],
    "confidence_score": 1.0
    }}

    **Input:** "This reminds me of the character Hark on in. He is so evil." (Assuming Book is 'Dune')
    **Output:**
    {{
    "page_number": null,
    "quote": null,
    "comment": "Reminds me of the character Harkonnen. He is so evil.",
    "tags": ["character", "connection"],
    "confidence_score": 0.95
    }}

    ### YOUR TASK
    Return ONLY the JSON object for the following transcript.
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Here is the raw text: {raw_text}"}
            ],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
        
    except Exception as e:
        print(f"Parsing error: {e}")
        return None
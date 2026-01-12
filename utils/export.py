import csv
import io
import zipfile
from datetime import date
from typing import Optional

from structures.book import Book
from structures.note import Note


# Only use callouts for tags that benefit from visual distinction
# Other tags (quote, remark, character) use plain blockquotes
TAG_CALLOUT_MAP = {
    "question": "question",
    "idea": "tip",
    "critique": "warning",
    "connection": "info",
}


def format_note_for_obsidian(note: Note) -> str:
    """Format a single note with tag-aware Obsidian formatting."""
    lines = []

    # Page header
    if note.page_number:
        lines.append(f"### Page {note.page_number}")
    else:
        lines.append("### Note")
    lines.append("")

    # Determine primary tag for callout formatting
    primary_tag = None
    if note.tags:
        for tag in note.tags:
            if tag in TAG_CALLOUT_MAP:
                primary_tag = tag
                break

    # Format content based on tag type
    has_quote = note.quote and note.quote.strip()
    has_comment = note.comment and note.comment.strip()

    if primary_tag and primary_tag in TAG_CALLOUT_MAP:
        # Use callout for special tags (question, idea, critique, connection)
        callout_type = TAG_CALLOUT_MAP[primary_tag]

        if has_quote and has_comment:
            lines.append(f"> [!{callout_type}]")
            lines.append(f"> {note.quote}")
            lines.append("")
            lines.append(note.comment)
        elif has_quote:
            lines.append(f"> [!{callout_type}]")
            lines.append(f"> {note.quote}")
        elif has_comment:
            lines.append(f"> [!{callout_type}]")
            lines.append(f"> {note.comment}")
        elif note.content:
            lines.append(f"> [!{callout_type}]")
            lines.append(f"> {note.content}")
    else:
        # Default: use [!quote] callout for quotes, plain text otherwise
        if has_quote:
            lines.append("> [!quote]")
            lines.append(f"> {note.quote}")
            if has_comment:
                lines.append("")
                lines.append(note.comment)
        elif has_comment:
            lines.append(note.comment)
        elif note.content:
            lines.append(note.content)

    lines.append("")

    # Tags as inline code
    if note.tags:
        tag_str = " ".join([f"`#{t}`" for t in note.tags])
        lines.append(tag_str)

    return "\n".join(lines)


def generate_book_markdown(book: Book, notes: list[Note]) -> str:
    """Generate a complete markdown file for a book with all its notes."""
    lines = []

    # YAML frontmatter
    lines.append("---")
    lines.append(f'title: "{book.title}"')
    lines.append(f'author: "{book.author}"')
    lines.append(f"exported: {date.today().isoformat()}")
    lines.append("tags: [book, marginal-ia]")
    lines.append("---")
    lines.append("")

    # Book header
    lines.append(f"# {book.title}")
    lines.append(f"*by {book.author}*")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Separate summary notes from regular notes
    summary_notes = [n for n in notes if n.tags and "summary" in n.tags]
    regular_notes = [n for n in notes if not n.tags or "summary" not in n.tags]

    # Sort regular notes by page number
    regular_notes.sort(key=lambda n: (n.page_number or 0))

    # Regular notes section
    if regular_notes:
        lines.append("## Notes")
        lines.append("")

        for note in regular_notes:
            lines.append(format_note_for_obsidian(note))
            lines.append("")
            lines.append("---")
            lines.append("")

    # Summary section (grouped at the end)
    if summary_notes:
        lines.append("## Summary")
        lines.append("")

        for note in summary_notes:
            lines.append(format_note_for_obsidian(note))
            lines.append("")
            lines.append("---")
            lines.append("")

    return "\n".join(lines)


def sanitize_filename(name: str) -> str:
    """Remove characters that are invalid in filenames."""
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        name = name.replace(char, '-')
    return name.strip()


def generate_obsidian_export(books: list[Book], notes: list[Note]) -> bytes:
    """Generate a ZIP file containing markdown files for all books with notes."""
    # Group notes by book_id
    notes_by_book: dict[Optional[str], list[Note]] = {}
    for note in notes:
        book_id = note.book_id
        if book_id not in notes_by_book:
            notes_by_book[book_id] = []
        notes_by_book[book_id].append(note)

    # Create book lookup
    book_lookup = {book.id: book for book in books}

    # Create ZIP in memory
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for book_id, book_notes in notes_by_book.items():
            if book_id and book_id in book_lookup:
                book = book_lookup[book_id]
                filename = f"{sanitize_filename(book.title)} - {sanitize_filename(book.author)}.md"
                content = generate_book_markdown(book, book_notes)
            else:
                # Notes without a book
                filename = "Unassigned Notes.md"
                placeholder_book = Book(title="Unassigned Notes", author="Unknown", id="")
                content = generate_book_markdown(placeholder_book, book_notes)

            zf.writestr(f"marginal-ia/{filename}", content)

    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def generate_csv_export(books: list[Book], notes: list[Note]) -> bytes:
    """Generate a CSV file with all notes (importable to Notion and other tools)."""
    # Create book lookup
    book_lookup = {book.id: book for book in books}

    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)

    # Header row
    writer.writerow([
        "Book Title",
        "Author",
        "Page",
        "Quote",
        "Comment",
        "Tags",
        "Content",
        "Confidence"
    ])

    # Sort notes by book, then by page
    sorted_notes = sorted(notes, key=lambda n: (
        book_lookup.get(n.book_id, Book(title="", author="")).title,
        n.page_number or 0
    ))

    for note in sorted_notes:
        book = book_lookup.get(note.book_id)
        book_title = book.title if book else "Unassigned"
        author = book.author if book else ""

        writer.writerow([
            book_title,
            author,
            note.page_number or "",
            note.quote or "",
            note.comment or "",
            ", ".join(note.tags) if note.tags else "",
            note.content or "",
            note.confidence_score or ""
        ])

    return csv_buffer.getvalue().encode('utf-8')

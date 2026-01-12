"""
ISBN lookup utilities using the Open Library API.
"""

import requests
from dataclasses import dataclass
from typing import Optional


@dataclass
class BookInfo:
    """Book information retrieved from ISBN lookup."""
    title: str
    author: str
    isbn: str
    cover_url: Optional[str] = None


def lookup_isbn(isbn: str) -> Optional[BookInfo]:
    """
    Look up book information by ISBN using Open Library API.

    Args:
        isbn: ISBN-10 or ISBN-13 (with or without dashes)

    Returns:
        BookInfo if found, None otherwise
    """
    # Clean ISBN (remove dashes and spaces)
    clean_isbn = isbn.replace("-", "").replace(" ", "").strip()

    if not clean_isbn:
        return None

    try:
        # Use Open Library Books API
        url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{clean_isbn}&format=json&jscmd=data"
        headers = {"User-Agent": "MarginalIA/1.0 (Book notes app)"}

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()

        # Check if we got a result
        key = f"ISBN:{clean_isbn}"
        if key not in data:
            return None

        book_data = data[key]

        # Extract title
        title = book_data.get("title", "Unknown Title")

        # Extract author(s)
        authors = book_data.get("authors", [])
        if authors:
            author = authors[0].get("name", "Unknown Author")
        else:
            author = "Unknown Author"

        # Extract cover URL (medium size)
        cover_url = None
        if "cover" in book_data:
            cover_url = book_data["cover"].get("medium")

        return BookInfo(
            title=title,
            author=author,
            isbn=clean_isbn,
            cover_url=cover_url
        )

    except requests.RequestException as e:
        print(f"ISBN lookup failed: {e}")
        return None
    except (KeyError, ValueError) as e:
        print(f"ISBN parsing failed: {e}")
        return None


def is_valid_isbn(isbn: str) -> bool:
    """
    Basic validation for ISBN-10 or ISBN-13.

    Args:
        isbn: ISBN string to validate

    Returns:
        True if valid format, False otherwise
    """
    clean = isbn.replace("-", "").replace(" ", "").strip()

    if len(clean) == 10:
        # ISBN-10: 9 digits + check digit (0-9 or X)
        return clean[:9].isdigit() and (clean[9].isdigit() or clean[9].upper() == "X")
    elif len(clean) == 13:
        # ISBN-13: 13 digits
        return clean.isdigit()

    return False

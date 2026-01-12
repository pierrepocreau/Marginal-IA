from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid

@dataclass
class Note:
    content: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    page_number: Optional[int] = None
    quote: Optional[str] = None
    comment: Optional[str] = None 
    book_id: Optional[str] = None
    tags: Optional[list[str]] = None
    confidence_score: Optional[float] = None
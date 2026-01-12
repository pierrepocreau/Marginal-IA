import uuid
from dataclasses import dataclass, field

@dataclass
class Book:
    title: str
    author: str    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


    def display_name(self):
        return f"{self.title} by {self.author}"

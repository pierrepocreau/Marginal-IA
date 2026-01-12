# Marginal-IA

A voice-to-note application for readers. Capture thoughts while reading physical books using voice recordings, and let AI structure them into organized, tagged notes.

## Demo

Try it out at [marginal-ia.com](https://marginal-ia.com)

> **Note**: The demo runs on free tiers of Railway, Groq, and Supabase, so you may occasionally hit rate limits. For heavy usage, consider self-hosting with your own API keys.

## Features

- **Voice Recording** - Record thoughts hands-free while reading
- **AI-Powered Parsing** - Automatically extracts quotes, comments, page numbers, and tags from transcriptions
- **Book Context Awareness** - AI corrects phonetic transcription errors using book/author context
- **ISBN Lookup** - Add books by entering their ISBN
- **Export Options** - Export to Obsidian (markdown with frontmatter) or CSV (Notion, Excel)
- **Multilingual** - Preserves the original language of your notes

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Supabase (PostgreSQL + Auth)
- **AI**: Groq (Whisper for transcription, Llama for parsing)
- **Book Data**: Open Library API

## Getting Started

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- Supabase account
- Groq API key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/marginal-ia.git
   cd marginal-ia
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Set up Supabase:
   - Create a new Supabase project
   - Run the schema from `supabase_schema.sql` in the SQL editor
   - Enable Row Level Security (RLS) policies are included in the schema

4. Configure environment variables:
   ```bash
   cp .env.example .env
   ```

   Fill in your credentials:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_anon_key
   GROQ_API_KEY=your_groq_api_key
   ```

5. Run the app:
   ```bash
   uv run streamlit run main.py
   ```

### Docker

1. Build the image:
   ```bash
   docker build -t marginal-ia .
   ```

2. Run the container:
   ```bash
   docker run -p 8501:8501 \
     -e SUPABASE_URL=your_supabase_url \
     -e SUPABASE_KEY=your_supabase_anon_key \
     -e GROQ_API_KEY=your_groq_api_key \
     marginal-ia
   ```

3. Open [http://localhost:8501](http://localhost:8501) in your browser

### Deployment on Streamlit Cloud

1. Push your code to GitHub
2. Connect your repo to [Streamlit Cloud](https://streamlit.io/cloud)
3. Add your environment variables in the Streamlit Cloud dashboard
4. The `packages.txt` file ensures system dependencies (ffmpeg, libzbar) are installed

## Project Structure

```
marginal-ia/
├── main.py                 # Entry point (auth + routing)
├── pages/
│   ├── login.py            # Authentication
│   ├── recorder.py         # Voice recording & AI parsing
│   ├── books.py            # Book management
│   └── notes.py            # Note viewing & export
├── structures/
│   ├── book.py             # Book dataclass
│   └── note.py             # Note dataclass
├── utils/
│   ├── db.py               # Database client
│   ├── sidebar.py          # Navigation
│   ├── parser.py           # AI note structuring
│   ├── isbn.py             # ISBN lookup
│   └── export.py           # Export functionality
├── supabase_schema.sql     # Database schema
├── pyproject.toml          # Dependencies
└── packages.txt            # System dependencies
```

## Usage

1. **Sign up/Login** with email and password
2. **Add a book** manually or by entering its ISBN
3. **Select the book** from the sidebar
4. **Record** your thoughts while reading
5. **Review** the AI-parsed note (quote, comment, tags)
6. **Export** your notes to Obsidian or CSV when ready

## Note Tags

The AI automatically assigns one or more tags to each note:

- `character` - Character analysis or observations
- `question` - Questions raised by the text
- `remark` - General remarks
- `quote` - Notable quotes worth remembering
- `summary` - Chapter or section summaries
- `idea` - Ideas sparked by the reading
- `connection` - Connections to other works or concepts
- `critique` - Critical analysis

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

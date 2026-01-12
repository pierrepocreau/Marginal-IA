# 1. Use Python 3.11 slim as the base
FROM python:3.11-slim-bookworm

# 2. Install the required system libraries (zbar & ffmpeg)
# We also clean up the apt cache to keep the image small
RUN apt-get update && apt-get install -y \
    gcc \
    libzbar0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 3. Install 'uv' by copying the binary from the official image
# This is the standard/cleanest way to install uv in Docker
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 4. Set working directory
WORKDIR /app

# 5. Copy dependency files first (for better caching)
COPY pyproject.toml uv.lock ./

# 6. Install dependencies using uv
# --frozen: ensures strict sync with uv.lock
# --no-cache: keeps the image small
RUN uv sync --frozen --no-cache

# 7. Add the virtual environment to the PATH
# uv creates the venv in .venv by default; this makes 'python' command use it automatically
ENV PATH="/app/.venv/bin:$PATH"

# 8. Copy the rest of your application code
COPY . .

# 9. Start the application
# Replace 'main.py' with your actual start script (e.g., bot.py)
CMD ["streamlit run", "main.py"]    
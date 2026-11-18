# Container image for the Mood Librarian API.
# The app binds $PORT (default 7860); hosts like Render inject their own $PORT.
FROM python:3.11-slim

WORKDIR /app

# Install dependencies first for better layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and the web UI.
COPY config.py tools.py agent.py main.py ./
COPY static ./static

# Run as a non-root user.
RUN useradd --create-home --uid 1000 appuser
USER appuser

# Default port; hosting platforms override $PORT at runtime.
ENV PORT=7860
EXPOSE 7860

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]

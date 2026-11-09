# Container image for the Mood Librarian API.
# Hugging Face Spaces (SDK=docker) expects the app on port 7860.
FROM python:3.11-slim

WORKDIR /app

# Install dependencies first for better layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code.
COPY config.py tools.py agent.py main.py ./

# Run as a non-root user.
RUN useradd --create-home --uid 1000 appuser
USER appuser

# Port (7860 for Hugging Face Spaces; override with $PORT elsewhere).
ENV PORT=7860
EXPOSE 7860

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]

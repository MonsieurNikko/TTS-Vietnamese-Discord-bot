FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    libopus0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/

# Copy environment files (single bot OR multi-bot)
# For single bot: .env
# For multi-bot: .env.bot1, .env.bot2, .env.bot3
COPY .env* ./

# Run bot
# Default: Multi-bot orchestrator (runs all bots in one process)
# To run single bot with specific config: set ENV variable (e.g., ENV=bot1)
CMD ["python", "src/tts_bot_multi.py"]

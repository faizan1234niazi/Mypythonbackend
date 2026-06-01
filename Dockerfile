FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y ffmpeg git && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy all files
COPY . /app

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Hugging Face default port
EXPOSE 7860

# Start Flask app
CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app"]

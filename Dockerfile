FROM python:3.10-slim

# Install system dependencies (ffmpeg is REQUIRED)
RUN apt-get update && apt-get install -y ffmpeg git

# Set working directory
WORKDIR /app

# Copy all files
COPY . /app

# Upgrade pip
RUN pip install --upgrade pip

# Install dependencies
RUN pip install -r requirements.txt

# Expose port
EXPOSE 8000

# Start server
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
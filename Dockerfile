FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code
COPY script.py .

# Expose the port your app runs on
EXPOSE 8111

# Run using Gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8111", "script:app"]

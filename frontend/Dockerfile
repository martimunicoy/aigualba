FROM python:3.11-slim
WORKDIR /app

# Install system dependencies that might be needed
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (will be overridden by volume mount in development)
COPY . .

# Run the application
CMD ["python", "app.py"]

# Use a lightweight Python image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    pkg-config \
    libcairo2-dev \
    python3-dev \
    libgirepository1.0-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Setting working directory 
WORKDIR /app

# Copy requirements first to to utilise Docker cache
COPY ./app/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the code 
COPY ./app /app

# Set environment variable for Python imports
ENV PYTHONPATH=/app

# Expose port for FastAPI app
EXPOSE 8000

# Command to run the app with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

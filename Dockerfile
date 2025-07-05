
FROM python:3.11-slim


RUN apt-get update && apt-get install -y \
    gcc \
    pkg-config \
    libcairo2-dev \
    python3-dev \
    libgirepository1.0-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app


COPY ./app/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

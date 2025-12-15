FROM python:3.9-slim

WORKDIR /app

COPY app/ ./app
COPY build_index.py ./
COPY .env ./
COPY requirements.txt ./
COPY app/static ./app/static
COPY app/templates ./app/templates

RUN pip install --upgrade pip && pip install -r requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
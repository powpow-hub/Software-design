FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH="/app/beauty_salon_project:${PYTHONPATH}"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
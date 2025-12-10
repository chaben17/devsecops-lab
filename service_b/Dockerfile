FROM python:3.13

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Attention : ici on utilise le port 8002
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]

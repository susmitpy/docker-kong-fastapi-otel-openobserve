FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY src/* /app

RUN apt-get update && apt-get install -y curl
RUN chmod +x /app/register_service.sh

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
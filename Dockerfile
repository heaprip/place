FROM docker.io/python:3.13.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workdir

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY template.html template.html

RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /workdir

USER appuser

EXPOSE 8080

CMD ["gunicorn", "app.app:app", "--bind", "0.0.0.0:8080", "--worker-class", "aiohttp.GunicornWebWorker"]

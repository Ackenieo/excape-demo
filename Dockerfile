FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY . /app

RUN chmod +x /app/docker/entrypoint.sh

RUN mkdir -p /app/uploads/avatars

RUN useradd -m -u 10001 appuser \
    && chown -R appuser:appuser /app
USER appuser

ENV FLASK_RUN_HOST=0.0.0.0 \
    FLASK_RUN_PORT=8888 \
    FLASK_DEBUG=false

EXPOSE 8888

ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8888", "run:app"]

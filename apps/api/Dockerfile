FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY apps/api/pyproject.toml /app/pyproject.toml
COPY apps/api/alembic.ini /app/alembic.ini
COPY apps/api/alembic /app/alembic
COPY apps/api/app /app/app
COPY apps/web/lib/demo/avert-demo.json /app/shared/avert-demo.json

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

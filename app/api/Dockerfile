FROM python:3.12-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH=/app

FROM base AS runtime
COPY *.py ./app/api/
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8123"]

FROM base AS test
COPY requirements-test.txt .
RUN pip install --no-cache-dir -r requirements-test.txt
COPY *.py ./app/api/
COPY tests/ ./app/api/tests/
CMD ["pytest", "-v", "app/api/tests/"]

FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the api source into app/api/ so `import app.api.*` resolves from /app
COPY . ./app/api/

# Ensure /app is on PYTHONPATH so `import app.api.*` works
ENV PYTHONPATH=/app

CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

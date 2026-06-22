FROM python:3.12-slim AS base
WORKDIR /app/db

FROM base AS runtime
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY alembic.ini .
COPY alembic/ ./alembic/
# used by the compose `migrate` service, which overrides: command: alembic upgrade head

FROM base AS test
COPY requirements-test.txt .
RUN pip install --no-cache-dir -r requirements-test.txt
# Copy ONLY the tests directory into the image. The migration (alembic/) is
# deliberately kept out of the test image so the schema characterization tests
# assert against the live database, never against the migration source.
COPY tests/ ./tests/
CMD ["pytest", "-v", "tests/", "--ignore=tests/test_migration_roundtrip.py"]

FROM base AS test-roundtrip
COPY requirements.txt requirements-test.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-test.txt
COPY alembic.ini .
COPY alembic/ ./alembic/
COPY tests/ ./tests/
CMD ["pytest", "-v", "tests/test_migration_roundtrip.py"]

# Stage 1: Build the React/Vite static bundle
FROM node:20-slim AS build

WORKDIR /app

# Install dependencies reproducibly using package-lock.json
COPY package.json package-lock.json ./
RUN npm ci

# Copy source and build
COPY index.html vite.config.js ./
COPY src/ ./src/
RUN npm run build
# Output: /app/dist/

# Stage 2: Python slim image for ETL and static file serving
FROM python:3.12-slim AS serve

# Install PyYAML for frontmatter parsing
RUN pip install --no-cache-dir PyYAML==6.0.2

# Served directory holds the static bundle and the generated data.json
ENV SERVED_DIR=/served
ENV REPO_ROOT=/repo

RUN mkdir -p /served

# Copy the built static bundle from stage 1
COPY --from=build /app/dist/ /served/

# Copy the ETL script
COPY etl.py /app/etl.py

# Entrypoint: run ETL first (writes data.json into SERVED_DIR), then serve
EXPOSE 8420
CMD python /app/etl.py && python -m http.server 8420 --directory /served --bind 0.0.0.0

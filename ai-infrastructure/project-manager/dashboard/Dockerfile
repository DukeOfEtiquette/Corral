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

# Install Python dependencies for ETL and file watching
RUN pip install --no-cache-dir PyYAML==6.0.2 watchdog==4.0.2

# Served directory holds the static bundle and the generated data.json
ENV SERVED_DIR=/served
ENV REPO_ROOT=/repo

RUN mkdir -p /served

# Copy the built static bundle from stage 1
COPY --from=build /app/dist/ /served/

# Copy the ETL script and entrypoint
COPY etl.py /app/etl.py
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Entrypoint: initial ETL build, background watcher, foreground HTTP server
EXPOSE 8420
CMD ["/app/entrypoint.sh"]

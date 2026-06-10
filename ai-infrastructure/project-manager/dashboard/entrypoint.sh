#!/bin/sh
# Entrypoint for the dashboard container.
#
# 1. Run the ETL once to produce the initial data.json.
# 2. Start the file watcher in the background. If it dies, serving continues.
# 3. Run the HTTP server in the foreground (keeps the container alive).

set -e

python /app/etl.py

# Launch the watcher as a background process. Failures are non-fatal to
# the container; the foreground server remains the process 1 replacement.
python /app/etl.py --watch &

exec python -m http.server 8420 --directory /served --bind 0.0.0.0

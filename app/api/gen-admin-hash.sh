#!/usr/bin/env bash
#
# gen-admin-hash.sh -- set the api service's admin bootstrap credentials in
# app/.env (gitignored; ADR-006/011). The password is argon2id-hashed via the
# api image, so no host Python is needed (ADR-003 compose run path); only the
# hash is stored, never the plaintext.
#
# Usage:
#   app/api/gen-admin-hash.sh --email me@example.com --password devpassword
#   app/api/gen-admin-hash.sh --password newpassword     # updates only the hash
#   app/api/gen-admin-hash.sh --email other@example.com  # updates only the email
#
# Each flag updates only its own key in app/.env and leaves the other untouched.
# `docker compose -f app/docker-compose.yml up api` reads app/.env directly.
# After the update, warns if either ADMIN_EMAIL or ADMIN_PASSWORD_HASH is unset.
#
# app/.env.example is the tracked template for app/.env; copy it and fill in
# ADMIN_EMAIL and ADMIN_PASSWORD_HASH before first use.
#
# Reseed gotcha: seed_admin() in app/api/admin_seed.py is idempotent -- it seeds
# the admin only if no users row with ADMIN_EMAIL already exists. Re-running this
# script with a new password and restarting the api does NOT update an already-seeded
# admin. To re-seed (e.g. to rotate the password), do a full volume reset first:
#   docker compose -f app/docker-compose.yml down -v
# then bring the stack back up and seed_admin() will seed with the new credentials.

set -euo pipefail

app_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
compose_file="$app_dir/docker-compose.yml"
env_file="$app_dir/.env"

email=""
password=""
have_email=0
have_password=0

while [ $# -gt 0 ]; do
  case "$1" in
    --email)     [ $# -ge 2 ] || { echo "error: --email needs a value" >&2; exit 2; }
                 email="$2"; have_email=1; shift 2 ;;
    --email=*)   email="${1#--email=}"; have_email=1; shift ;;
    --password)  [ $# -ge 2 ] || { echo "error: --password needs a value" >&2; exit 2; }
                 password="$2"; have_password=1; shift 2 ;;
    --password=*) password="${1#--password=}"; have_password=1; shift ;;
    -h|--help)   cat >&2 <<'EOF'
Usage: gen-admin-hash.sh [--email EMAIL] [--password PASSWORD]
  Updates app/.env (gitignored) with the api admin bootstrap credentials.
  --password is argon2id-hashed via the api image; --email is stored verbatim.
  Each flag updates only its key; the other is preserved. Warns if either is unset.
EOF
                 exit 0 ;;
    *)           echo "error: unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [ "$have_email" -eq 0 ] && [ "$have_password" -eq 0 ]; then
  echo "error: pass --email and/or --password (see --help)" >&2
  exit 2
fi

# Upsert KEY=VALUE into env_file, preserving every other line (comments included).
# VALUE has $ escaped to $$ so docker compose does NOT interpolate it: an argon2id
# hash contains $ (e.g. $argon2id$v=19$...$salt$hash), which compose would
# otherwise read as $variables and blank out, corrupting the hash. Compose
# un-escapes $$ back to a literal $ when it sets the container env. Values are
# single-line (no newlines).
upsert() {
  local key="$1" value tmp line
  value="$(printf '%s' "$2" | sed 's/[$]/$$/g')"
  touch "$env_file"
  if grep -q "^${key}=" "$env_file"; then
    tmp="$(mktemp)"
    while IFS= read -r line || [ -n "$line" ]; do
      case "$line" in
        "${key}="*) printf '%s=%s\n' "$key" "$value" ;;
        *)          printf '%s\n' "$line" ;;
      esac
    done < "$env_file" > "$tmp"
    mv "$tmp" "$env_file"
  else
    printf '%s=%s\n' "$key" "$value" >> "$env_file"
  fi
}

if [ "$have_email" -eq 1 ]; then
  upsert ADMIN_EMAIL "$email"
  echo "set ADMIN_EMAIL in $env_file"
fi

if [ "$have_password" -eq 1 ]; then
  pw_hash="$(docker compose -f "$compose_file" run --rm --no-deps -T api \
    python -c 'import sys; from argon2 import PasswordHasher; print(PasswordHasher().hash(sys.argv[1]))' "$password")"
  upsert ADMIN_PASSWORD_HASH "$pw_hash"
  echo "set ADMIN_PASSWORD_HASH in $env_file"
fi

# Completeness check: warn (do not fail) if either credential is still unset.
missing=()
grep -qE '^ADMIN_EMAIL=.+'         "$env_file" 2>/dev/null || missing+=("ADMIN_EMAIL")
grep -qE '^ADMIN_PASSWORD_HASH=.+' "$env_file" 2>/dev/null || missing+=("ADMIN_PASSWORD_HASH")
if [ "${#missing[@]}" -gt 0 ]; then
  echo "WARNING: ${missing[*]} not yet set in $env_file; the api service will refuse to start until it is." >&2
fi

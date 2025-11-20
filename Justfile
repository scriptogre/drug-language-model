default:
    @just --list

setup:
    #!/usr/bin/env bash
    set -euo pipefail
    mkdir -p data
    cd data
    [ -f "01-drugcentral.dump.11012023.sql.gz" ] || curl -L -o 01-drugcentral.dump.11012023.sql.gz https://unmtid-dbs.net/download/drugcentral.dump.11012023.sql.gz

build:
    docker compose build

up:
    docker compose up -d

down:
    docker compose down

logs:
    docker compose logs -f

psql:
    docker compose exec postgres psql -U postgres -d drugcentral

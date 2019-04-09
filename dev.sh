#!/usr/bin/env bash

# Methods
# --------------------------------------------------------------------------------------
docker-compose () {
    command docker-compose -f docker/dev-compose.yml "$@"
}

docker-down () {
    docker-compose down -v
}

docker-pull () {
    docker-compose pull
}

docker-logs () {
    docker-compose logs -ft --tail=100 "$@"
}

docker-restart () {
    docker-compose up -d --build --no-deps "$@"
}


# Parse Script Arguments
# ----------------------


# Main
# ----------------------
docker-compose up -d

trap 'trap "" INT; docker-compose stop -t 20' EXIT

while true; do
    echo "Ctrl-C once to restart Flask; twice rapidly to exit."
    (cd core && FLASK_ENV=development FLASK_APP=core.application ../venv/bin/flask run "$@")
    docker-restart
    sleep 1
done

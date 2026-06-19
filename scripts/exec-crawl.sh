#!/usr/bin/env bash
# Run a Python script *inside* the crawl4ai container.
#
# This is useful if you need direct access to the crawl4ai Python library
# rather than the REST API.  The script must live under ./scripts/ (which
# is mounted at /scripts inside the container).
#
# Usage:  ./scripts/exec-crawl.sh my_script.py [args...]

set -e
container_id=$(docker compose ps -q crawl4ai 2>/dev/null)
if [ -z "$container_id" ]; then
  echo "Error: crawl4ai container is not running.  Start it with:  docker compose up -d"
  exit 1
fi
docker exec -i "$container_id" python3 /scripts/"$@"

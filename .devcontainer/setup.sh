#!/usr/bin/env bash
# Codespace creation setup for NetOps Copilot. Runs once at creation.
# Best effort on the Batfish image: if Docker is unavailable here, the
# script still succeeds and the web app runs in recorded mode; the
# manual fallback is one docker command (see .devcontainer/README.md).
set -u
cd "$(dirname "$0")/.."

python3 -m pip install --upgrade pip pybatfish

if command -v docker >/dev/null 2>&1; then
  echo "Pulling the official Batfish image (batfish/allinone)..."
  docker pull batfish/allinone \
    && echo "Batfish image ready." \
    || echo "WARNING: could not pull batfish/allinone. Live mode needs: docker run -d --name batfish -p 9996:9996 batfish/allinone"
else
  echo "WARNING: docker is not available in this container. Live mode needs a Batfish service; see .devcontainer/README.md. Recorded mode works without it."
fi

chmod +x scripts/start-live.sh
echo "Codespace setup done."

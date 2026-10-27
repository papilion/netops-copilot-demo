# NetOps Copilot in GitHub Codespaces

This folder makes the live demo runnable from github.com alone, with
no local install, no WSL, and no manual Java or jar setup.

## What creation does automatically

- Base image: Python 3.12, with Java 21 and Docker-in-Docker features.
- `postCreateCommand` (`.devcontainer/setup.sh`): installs `pybatfish`
  with pip and pulls the official Batfish image `batfish/allinone`
  (documented in the Batfish README as `docker pull batfish/allinone`,
  run with `-p 9996:9996`). No jar is stored in this repo.
- `postStartCommand` (`scripts/start-live.sh`): starts the Batfish
  container if Docker is available, then starts the web app on port
  8000 (bound to 127.0.0.1 inside the codespace; Codespaces port
  forwarding is the only external access).

## If Docker is unavailable in the codespace

This was not verified from a machine without Codespaces access, so
treat it as the one remaining manual step, not as an automatic one:

```text
docker run -d --name batfish -p 9996:9996 batfish/allinone
bash scripts/start-live.sh
```

Then open the forwarded port 8000. If Batfish is still not up, the
web app returns HTTP 503 for Live mode (with the start command) and
does not silently fall back — use Recorded replay instead, which
needs no Batfish at all.

## Port visibility

Keep the forwarded port 8000 **Private** (the Codespaces default for
your own codespace). Do not change it to Public: this demo web app
has no authentication, binds 127.0.0.1 only, and never applies a
change to a router. It is a validation demo, not a shared service.

## What is NOT verified here

A real Codespaces boot was not run from the development VM that
built this repo, so the first codespace creation is the proof run:
if the Batfish container starts, Live mode works end to end; if it
does not, the fallback above is the only manual step, and recorded
mode still works with zero setup.

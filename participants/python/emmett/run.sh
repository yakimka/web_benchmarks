#!/usr/bin/env sh

emmett serve \
  --threading-mode="runtime" \
  --workers=${WEB_CONCURRENCY:-1} \
  --host=0.0.0.0 \
  --port=8000 \
  --log-level=info \
  --backlog=16384 \
  --no-ws

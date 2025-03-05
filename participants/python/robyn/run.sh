#!/usr/bin/env sh

python -m robyn \
  server.py \
  --fast \
  --processes=${WEB_CONCURRENCY:-1} \
  --workers=2 \
  --log-level=WARN

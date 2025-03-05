#!/usr/bin/env sh

python -m robyn \
  server.py \
  --fast \
  --processes=4 \
  --workers=2 \
  --log-level=WARN

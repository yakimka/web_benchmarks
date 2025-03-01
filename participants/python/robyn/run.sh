#!/usr/bin/env sh

python -m robyn \
  server.py \
  --processes=4 \
  --workers=9 \
  --log-level=WARN

#!/usr/bin/env sh

granian server_asgi:app \
  --interface=asgi \
  --workers=${WEB_CONCURRENCY:-1} \
  --host=0.0.0.0 \
  --port=8000 \
  --loop=uvloop \
  --log-level=info \
  --no-access-log

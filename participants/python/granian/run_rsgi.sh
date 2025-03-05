#!/usr/bin/env sh

granian server_rsgi:app \
  --interface=rsgi \
  --workers=${WEB_CONCURRENCY:-1} \
  --host=0.0.0.0 \
  --port=8000 \
  --loop=uvloop \
  --log-level=info \
  --no-access-log

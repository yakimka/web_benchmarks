#!/usr/bin/env bash

gunicorn --pid=gunicorn.pid \
  server:application \
  --worker-class=${WORKER_CLASS:-"sync"} \
  --workers=${WEB_CONCURRENCY:-1} \
  --threads=${THREADS:-1} \
  --bind=0.0.0.0:8000 \
  --keep-alive=120

#!/usr/bin/env bash

if [ "${ASYNC_MODE}" == "1" ]; then
  uvicorn server.asgi:application \
      --host=0.0.0.0 \
      --port=8000 \
      --loop=uvloop \
      --http=httptools \
      --log-level=info \
      --no-access-log \
      --timeout-keep-alive=120
else
  gunicorn --pid=gunicorn.pid \
    server.wsgi:application \
    --worker-class=sync \
    --workers=10 \
    --threads=${THREADS:-1} \
    --bind=0.0.0.0:8000 \
    --keep-alive=120
fi

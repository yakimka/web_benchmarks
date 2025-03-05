#!/usr/bin/env sh

uvicorn server:app \
    --host=0.0.0.0 \
    --port=8000 \
    --loop=uvloop \
    --http=httptools \
    --log-level=info \
    --no-access-log \
    --timeout-keep-alive=120

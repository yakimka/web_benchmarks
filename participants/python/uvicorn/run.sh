#!/usr/bin/env sh

uvicorn server:main \
    --host=0.0.0.0 \
    --port=8000 \
    --loop=${LOOP} \
    --http=${HTTP} \
    --log-level=${LOG_LEVEL} \
    --no-access-log \
    --timeout-keep-alive=120

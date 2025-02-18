ARG PYTHON_IMAGE=python:3.12.7-slim
# pypy:3.10-7.3.17-slim
FROM $PYTHON_IMAGE

COPY requirements.base.txt /app/requirements.base.txt
COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY server.py /app/server.py
COPY run.sh /app/run.sh

ENV WEB_CONCURRENCY=1
ENV LOG_LEVEL="info"
ENV LOOP="uvloop"
ENV JSON_LIBRARY="orjson"
ENV HTTP="httptools"

EXPOSE 8000
WORKDIR /app

CMD ["./run.sh"]

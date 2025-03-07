FROM python:3.12.7-slim

COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY server.py run.sh  /app/

ENV WEB_CONCURRENCY=1

EXPOSE 8000
WORKDIR /app

CMD ["./run.sh"]

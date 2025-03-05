FROM python:3.12.7-slim

COPY requirements.base.txt requirements.txt /app/

RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && apt-get autoremove -y

RUN pip install -r /app/requirements.txt

COPY server.py run.sh /app/

ENV WEB_CONCURRENCY=1

EXPOSE 8000
WORKDIR /app

CMD ["./run.sh"]

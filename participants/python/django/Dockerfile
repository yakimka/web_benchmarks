FROM python:3.12.7-slim

COPY requirements.txt /app/requirements.txt

RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && apt-get autoremove -y

RUN pip install -r /app/requirements.txt

COPY . /app/

ENV WEB_CONCURRENCY=4

EXPOSE 8000
WORKDIR /app

CMD ["./run.sh"]

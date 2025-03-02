FROM python:3.12.7-slim

COPY requirements.txt requirements.base.txt /app/

RUN apt-get update && apt-get install -y --no-install-recommends \
    libuv1-dev libssl-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && apt-get autoremove -y

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY server.py /app/server.py

EXPOSE 8000
WORKDIR /app

CMD [ "python", "./server.py" ]

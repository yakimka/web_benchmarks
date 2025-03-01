FROM python:3.12.7-slim

COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY server.py /app/server.py
COPY run.sh /app/run.sh

EXPOSE 8000
WORKDIR /app

CMD ["./run.sh"]

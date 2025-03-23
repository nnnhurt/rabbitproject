
FROM python:3.10.5-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

ENV RABBIT_HOST=rabbitmq
ENV CASSANDRA_HOSTS=cassandra
ENV CASSANDRA_KEYSPACE=my_keyspace
CMD ["python3", "consumer.py"]

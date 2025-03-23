import asyncio
import os
from cassandra.cluster import Cluster
from cassandra.query import PreparedStatement
from rabbit import channel_pool
import aio_pika


QUEUE = "my_queue"
EXCHANGE = "my_exchange"
ROUTING_KEY = "my_routing_key"

CASSANDRA_HOSTS = ['cassandra']
CASSANDRA_PORT = int(os.getenv('CASSANDRA_PORT', 9042))
TABLE_NAME = os.getenv('CASSANDRA_TABLE_NAME', 'default_table')
CASSANDRA_KEYSPACE = "simple_keyspace"


def setup_cassandra():
    try:
        cluster = Cluster(contact_points=CASSANDRA_HOSTS, port=CASSANDRA_PORT)
        session = cluster.connect()

        session.execute(f"""
            CREATE KEYSPACE IF NOT EXISTS {CASSANDRA_KEYSPACE} 
            WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}};
        """)
        session.set_keyspace(CASSANDRA_KEYSPACE)

        session.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                id UUID PRIMARY KEY,
                message TEXT
            );
        """)

        insert_stmt = session.prepare(f"""
            INSERT INTO {TABLE_NAME} (id, message)
            VALUES (uuid(), ?);
        """)

        print("Cassandra успешно настроена.")
        return session, insert_stmt

    except Exception as e:
        print(f"Ошибка подключения к Cassandra: {str(e)}")
        raise

async def process_message(message: aio_pika.IncomingMessage, session, insert_stmt: PreparedStatement):
    async with message.process():
        try:
            decoded_message = message.body.decode()
            session.execute(insert_stmt, (decoded_message,))
            print(f"Сообщение сохранено в Cassandra: {decoded_message}")
        except Exception as e:
            print(f"Ошибка сохранения сообщения: {str(e)}")
            raise

async def main():
    if not TABLE_NAME:
        print("Ошибка: TABLE_NAME не задана в переменных окружения.")
        return

    try:
        session, insert_stmt = setup_cassandra()
    except Exception as e:
        print("Не удалось настроить Cassandra. Завершение работы.")
        return


    async with channel_pool.acquire() as channel:
        try:
            queue = await channel.declare_queue(QUEUE, durable=True)
            exchange = await channel.declare_exchange(EXCHANGE, type=aio_pika.ExchangeType.DIRECT, durable=True)
            
            await queue.bind(exchange, routing_key=ROUTING_KEY)
            
            print("Ожидание сообщений из RabbitMQ...")
            
            await queue.consume(lambda msg: process_message(msg, session, insert_stmt))
        
        except Exception as e:
            print(f"Ошибка работы с RabbitMQ: {str(e)}")
            raise

if __name__ == "__main__":
    asyncio.run(main())

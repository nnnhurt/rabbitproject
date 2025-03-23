import asyncio
from rabbit import channel_pool
import aio_pika

EXCHANGE_NAME = "my_exchange"
QUEUE_NAME = "my_queue"
ROUTING_KEY = "my_routing_key"

async def send_message(message):
    async with channel_pool.acquire() as channel:
        exchange = await channel.declare_exchange(EXCHANGE_NAME, type=aio_pika.ExchangeType.DIRECT, durable=True)
        queue = await channel.declare_queue(QUEUE_NAME, durable=True)
        await queue.bind(exchange, routing_key=ROUTING_KEY)
        
        await exchange.publish(
            aio_pika.Message(body=message.encode()),
            routing_key=ROUTING_KEY
        )
        print(f"Отправлено сообщение: {message}")

async def main():
    try:
        with open("input.txt", "r") as file:
            for line in file:
                line = line.strip()
                if line:
                    await send_message(line)
    except FileNotFoundError:
        print("Файл input.txt не найден.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

asyncio.run(main())

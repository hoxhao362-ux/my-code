import asyncio
from aiokafka import AIOKafkaProducer
async def test():
    try:
        p = AIOKafkaProducer(bootstrap_servers='localhost:9092')
        await p.start()
        print('Kafka connected')
        await p.stop()
    except Exception as e:
        print('Error:', e)
asyncio.run(test())

import asyncio
import redis.asyncio as redis
async def test():
    r = redis.Redis(host='localhost', port=6379, password='wzut123', socket_timeout=5)
    try:
        print(await r.ping())
    except Exception as e:
        print(e)
asyncio.run(test())

from redis.asyncio import Redis

# redis_client = Redis(host="localhost", port=6379, db=0)
redis_client = Redis(host="products_redis", port=6379, db=0)

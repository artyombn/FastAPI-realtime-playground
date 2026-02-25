import aioredis

redis_client = aioredis.StrictRedis(host="products_redis", port=6379, db=0)

import logging

from redis.asyncio import Redis

from products.core.entities import ProductCreate, ProductResponse
from products.database.base import redis_client

logger = logging.getLogger("products_app")


class RedisRepository:
    def __init__(self, client: Redis):
        self.client = client

    async def save(self, key: str, product: ProductCreate):

        await self.client.set(key, product.model_dump_json())

    async def list(self, key_pattern: str):
        cursor = 0
        keys = []
        while True:
            cursor, partial_keys = await self.client.scan(
                cursor=cursor, match=key_pattern, count=10
            )
            keys.extend(partial_keys)
            if cursor == 0:
                break

        result = []

        for key in keys:
            data = await self.client.get(key)
            if data:
                result.append(ProductResponse.parse_raw(data))
        return result


redis_repository = RedisRepository(redis_client)

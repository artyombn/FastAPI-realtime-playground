import json

import aioredis

from products.core.entities import ProductCreate
from products.database.base import redis_client


class RedisRepository:
    def __init__(self, client: aioredis.StrictRedis):
        self.client = client

    async def save(self, key: str, product: ProductCreate):
        await self.client.set(key, product.model_dump_json())

    async def list(self, key_pattern: str):
        cursor = 0
        keys = []
        while True:
            cursor, partial_keys = await self.client.scan(
                cursor=cursor, match=key_pattern
            )
            keys.extend(partial_keys)
            if cursor == 0:
                break

        return [ProductCreate.parse_raw(await self.client.get(key)) for key in keys]


redis_repository = RedisRepository(redis_client)

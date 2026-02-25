import asyncio
from datetime import date, timedelta

import httpx

from products.core.entities import (
    ProductResponse,
    ProductCreate,
    PriceHistory,
)
from products.database.redis_repository import redis_repository


class ProductService:
    """
    Product Service to manage products
    """

    def __init__(self, repository):
        self.repository = repository

    @staticmethod
    async def get_usd_rates(_date: date):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange",
                params={"json": True, "date": _date.strftime("%Y%m%d")},
            )
        usd_rate = next(
            (item for item in response.json() if item["cc"] == "USD"), {"rate": 0}
        )
        return usd_rate["rate"]

    async def add(self, product: ProductCreate):
        today = date.today()
        price_data = {}

        for i in range(7):
            day = today - timedelta(days=i)
            usd_rates = await self.get_usd_rates(day)
            price_data[day.strftime("%Y-%m-%d")] = usd_rates * product.origin_price
            # await asyncio.sleep(10)

        history = PriceHistory(prices=price_data)
        product.price_history = history
        await self.repository.save(f"product_{product.id}", product)

    async def get_by_id(self, product_id: int) -> ProductResponse:
        return await self.repository.get_by_id(product_id)

    async def delete(self, product_id: int) -> None:
        await self.repository.delete(product_id)

    async def list(self) -> list[ProductResponse]:
        return await self.repository.list("product_*")


product_service = ProductService(redis_repository)

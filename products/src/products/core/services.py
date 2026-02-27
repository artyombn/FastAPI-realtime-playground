import logging
from datetime import date, timedelta

import httpx

from products.core.entities import (
    ProductResponse,
    ProductCreate,
    PriceHistory,
)
from products.database.redis_repository import redis_repository

logger = logging.getLogger("products_app")


class ProductService:
    """
    Product Service to manage products
    """

    def __init__(self, repository):
        self.repository = repository

    @staticmethod
    async def get_usd_rates(_date: str):
        async with httpx.AsyncClient() as client:
            logger.debug(
                f"----> LINK <-----  https://www.cbr-xml-daily.ru/archive/{_date}/daily_json.js"
            )

            response = await client.get(
                f"https://www.cbr-xml-daily.ru/archive/{_date}/daily_json.js",
            )
            if response.status_code != 200:
                return None
        usd_rate = next(
            (item for item in response.json()["Valute"].items() if item[0] == "USD"),
        )
        return usd_rate

    async def add(self, product: ProductCreate):
        today = date.today()
        price_data = {}

        for i in range(1, 30):
            day = today - timedelta(days=i)
            formatted_day = day.strftime("%Y/%m/%d")
            usd_rates = await self.get_usd_rates(formatted_day)

            if usd_rates is None:
                continue
            usd_rate = usd_rates[1]["Value"]
            price_data[formatted_day.replace("/", "-")] = (
                usd_rate * product.origin_price
            )

        logger.debug(f"PRICE_DATA = {price_data}")

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

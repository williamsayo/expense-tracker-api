import httpx
from decimal import Decimal
from typing import cast

type Rates = dict[str, Decimal]

class FxService:
    async def get_rates(self, currency: str) -> Rates:
        url = f"https://api.fxapi.app/api/{currency}.json"

        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data: dict = response.json()
            return cast(Rates, data.get("rates"))

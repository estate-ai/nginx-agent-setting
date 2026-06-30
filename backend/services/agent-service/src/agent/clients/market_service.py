from __future__ import annotations

from typing import Any

import httpx

from agent.core.config import settings


class MarketServiceClient:
    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        async with httpx.AsyncClient(
            base_url=settings.market_service_url,
            timeout=settings.service_request_timeout_seconds,
        ) as client:
            response = await client.request(method, path, params=params)
            response.raise_for_status()
            body: Any = response.json()
        if not isinstance(body, dict):
            raise RuntimeError("market-service 응답 형식이 올바르지 않습니다.")
        return body

    async def search_areas(
        self,
        *,
        keyword: str | None,
        industry_code: str | None,
        period: str = "latest",
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"period": period}
        if keyword is not None:
            params["keyword"] = keyword
        if industry_code is not None:
            params["industryCode"] = industry_code

        body = await self._request("GET", "/api/v1/market-search/areas", params=params)
        data = body.get("data")
        if not isinstance(data, dict):
            raise RuntimeError("market-service 검색 응답 data 형식이 올바르지 않습니다.")
        return data


market_service_client = MarketServiceClient()

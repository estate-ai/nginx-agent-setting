from __future__ import annotations

from typing import Any

import httpx

from agent.core.config import settings


class FranchiseServiceClient:
    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        async with httpx.AsyncClient(
            base_url=settings.franchise_service_url,
            timeout=settings.service_request_timeout_seconds,
        ) as client:
            response = await client.request(method, path, params=params)
            response.raise_for_status()
            body: Any = response.json()
        if not isinstance(body, dict):
            raise RuntimeError("franchise-service 응답 형식이 올바르지 않습니다.")
        return body

    async def get_franchises(
        self,
        *,
        industry_code: str | None,
        size: int,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"size": size}
        if industry_code is not None:
            params["industryCode"] = industry_code
        return await self._request("GET", "/api/v1/franchises", params=params)


franchise_service_client = FranchiseServiceClient()

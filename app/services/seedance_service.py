"""
Seedance（字节跳动方舟 Ark）API 服务
封装 Seedance 视频生成任务的创建与查询
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx

from app.config import settings
from app.utils.exceptions import SeedanceAPIException, ConfigurationException


DEFAULT_SEEDANCE_MODEL_ID = "doubao-seedance-1-5-pro-251215"


class SeedanceService:
    """Seedance API 服务类"""

    def __init__(self):
        self.base_url = (settings.seedance_base_url or "").rstrip("/")
        self.api_key = settings.seedance_api_key or ""

    def _auth_headers(self) -> Dict[str, str]:
        if not self.api_key:
            raise ConfigurationException(
                "Seedance API Key 未配置",
                details={"config_key": "seedance.api_key"},
            )
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    async def create_task(
        self,
        content: List[Dict[str, Any]],
        *,
        model: str,
        generate_audio: bool = True,
    ) -> Dict[str, Any]:
        """
        创建视频生成任务（异步）

        Returns:
            Dict: API 响应数据（包含 id）
        """
        url = f"{self.base_url}/api/v3/contents/generations/tasks"
        model = (model or "").strip() or DEFAULT_SEEDANCE_MODEL_ID
        payload: Dict[str, Any] = {
            "model": model,
            "content": content,
            "generate_audio": bool(generate_audio),
        }
        return await self._make_request("POST", url, json=payload)

    async def query_task(self, task_id: str) -> Dict[str, Any]:
        """
        查询视频生成任务状态

        Returns:
            Dict: API 响应数据
        """
        url = f"{self.base_url}/api/v3/contents/generations/tasks/{task_id}"
        return await self._make_request("GET", url)

    async def _make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        if headers is None:
            headers = self._auth_headers()
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.request(method, url, headers=headers, **kwargs)

            try:
                data = response.json()
            except Exception:
                raise SeedanceAPIException(
                    f"Seedance API 响应非 JSON，状态码: {response.status_code}",
                    details={"response_text": response.text},
                )

            if response.status_code not in (200, 201):
                error = data.get("error") if isinstance(data, dict) else None
                message = None
                code = None
                if isinstance(error, dict):
                    code = error.get("code")
                    message = error.get("message")
                if not message and isinstance(data, dict):
                    message = data.get("message") or data.get("error_message")
                    code = code or data.get("code") or data.get("error_code")

                raise SeedanceAPIException(
                    f"Seedance API 调用失败: {message or '未知错误'}",
                    details={
                        "status_code": response.status_code,
                        "error_code": code,
                        "response": data,
                    },
                )

            if not isinstance(data, dict):
                raise SeedanceAPIException(
                    "Seedance API 响应格式错误：顶层不是对象",
                    details={"response": data},
                )

            return data

        except httpx.HTTPError as e:
            raise SeedanceAPIException(f"HTTP请求失败: {str(e)}")
        except SeedanceAPIException:
            raise
        except ConfigurationException:
            raise
        except Exception as e:
            raise SeedanceAPIException(f"请求异常: {str(e)}")


seedance_service = SeedanceService()

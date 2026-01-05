"""
OpenAI Videos API 服务（Sora）
封装 OpenAI 视频生成：create / remix / retrieve / content download
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from app.config import settings
from app.utils.exceptions import OpenAIAPIException, ConfigurationException


class OpenAIVideoService:
    """OpenAI Videos API 服务类"""

    def __init__(self):
        self.base_url = (settings.openai_base_url or "").rstrip("/")
        self.api_key = settings.openai_api_key or ""

    def _auth_headers(self, *, content_type: Optional[str] = None) -> Dict[str, str]:
        if not self.api_key:
            raise ConfigurationException(
                "OpenAI API Key 未配置",
                details={"config_key": "openai.api_key"},
            )
        headers: Dict[str, str] = {"Authorization": f"Bearer {self.api_key}"}
        if content_type:
            headers["Content-Type"] = content_type
        return headers

    async def create_video(
        self,
        *,
        prompt: str,
        model: str,
        seconds: str,
        size: str,
        input_reference: Optional[tuple[str, bytes, str]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/videos"

        payload: Dict[str, str] = {
            "prompt": prompt,
            "model": model,
            "seconds": seconds,
            "size": size,
        }

        # OpenAI Videos API 仅接受 multipart/form-data 或 application/json
        # - 有 input_reference 时使用 multipart/form-data
        # - 无 input_reference 时使用 JSON（避免 httpx 默认的 x-www-form-urlencoded）
        if input_reference is not None:
            filename, content, content_type = input_reference
            return await self._make_json_request(
                "POST",
                url,
                data=payload,
                files={"input_reference": (filename, content, content_type)},
                timeout=60.0,
            )

        return await self._make_json_request(
            "POST",
            url,
            json=payload,
            timeout=60.0,
        )

    async def remix_video(self, *, video_id: str, prompt: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/videos/{video_id}/remix"
        return await self._make_json_request(
            "POST",
            url,
            json={"prompt": prompt},
            timeout=60.0,
        )

    async def retrieve_video(self, *, video_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/videos/{video_id}"
        return await self._make_json_request("GET", url, timeout=30.0)

    async def download_video_content(self, *, video_id: str, variant: Optional[str] = None) -> bytes:
        url = f"{self.base_url}/v1/videos/{video_id}/content"
        params = {}
        if variant:
            params["variant"] = variant

        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.get(url, headers=self._auth_headers(), params=params)

            if response.status_code != 200:
                # 尝试解析 OpenAI 标准错误结构
                try:
                    data = response.json()
                except Exception:
                    raise OpenAIAPIException(
                        f"OpenAI 内容下载失败，状态码: {response.status_code}",
                        details={"response_text": response.text},
                    )

                error = data.get("error") if isinstance(data, dict) else None
                message = None
                code = None
                if isinstance(error, dict):
                    message = error.get("message")
                    code = error.get("code")
                raise OpenAIAPIException(
                    f"OpenAI 内容下载失败: {message or '未知错误'}",
                    details={"status_code": response.status_code, "error_code": code, "response": data},
                )

            return response.content

        except httpx.HTTPError as e:
            raise OpenAIAPIException(f"HTTP请求失败: {str(e)}")
        except ConfigurationException:
            raise
        except OpenAIAPIException:
            raise
        except Exception as e:
            raise OpenAIAPIException(f"请求异常: {str(e)}")

    async def _make_json_request(
        self,
        method: str,
        url: str,
        *,
        timeout: float,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        if headers is None:
            headers = self._auth_headers()

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.request(method, url, headers=headers, **kwargs)

            try:
                data = response.json()
            except Exception:
                raise OpenAIAPIException(
                    f"OpenAI API 响应非 JSON，状态码: {response.status_code}",
                    details={"response_text": response.text},
                )

            if response.status_code not in (200, 201):
                error = data.get("error") if isinstance(data, dict) else None
                message = None
                code = None
                if isinstance(error, dict):
                    message = error.get("message")
                    code = error.get("code")
                raise OpenAIAPIException(
                    f"OpenAI API 调用失败: {message or '未知错误'}",
                    details={"status_code": response.status_code, "error_code": code, "response": data},
                )

            if not isinstance(data, dict):
                raise OpenAIAPIException(
                    "OpenAI API 响应格式错误：顶层不是对象",
                    details={"response": data},
                )

            return data

        except httpx.HTTPError as e:
            raise OpenAIAPIException(f"HTTP请求失败: {str(e)}")
        except ConfigurationException:
            raise
        except OpenAIAPIException:
            raise
        except Exception as e:
            raise OpenAIAPIException(f"请求异常: {str(e)}")


openai_video_service = OpenAIVideoService()

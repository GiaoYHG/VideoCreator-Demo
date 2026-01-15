"""
Google Veo 3.1（Gemini API）服务
封装：generate_videos / operations.get / files.download

说明：
- 使用官方 google-genai Python SDK（同步），通过 anyio.to_thread 包装为异步。
- SDK 依赖为可选；未安装或未配置 api_key 时抛 ConfigurationException。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import io
import os
import tempfile

import anyio

from app.config import settings
from app.utils.exceptions import ConfigurationException, GoogleVeoAPIException


def _safe_str(value: Any) -> str:
    try:
        return str(value)
    except Exception:
        return repr(value)


class VeoService:
    """Veo 3.1 API 服务类（基于 google-genai SDK）"""

    def _require_api_key(self) -> str:
        api_key = (settings.google_api_key or "").strip()
        if not api_key:
            raise ConfigurationException(
                "Google API Key 未配置",
                details={"config_key": "google.api_key"},
            )
        return api_key

    def _import_sdk(self):
        try:
            from google import genai  # type: ignore
            from google.genai import types  # type: ignore
            return genai, types
        except Exception as e:
            raise ConfigurationException(
                "缺少依赖 google-genai（用于 Veo 3.1）",
                details={"pip": "pip install google-genai", "error": _safe_str(e)},
            )

    def _client(self):
        api_key = self._require_api_key()
        genai, _ = self._import_sdk()

        # 兼容 SDK 通过环境变量读取 key 的方式
        os.environ["GOOGLE_API_KEY"] = api_key

        try:
            return genai.Client()
        except Exception as e:
            raise GoogleVeoAPIException("Gemini Client 初始化失败", details={"error": _safe_str(e)})

    @staticmethod
    def _extract_video_bytes(video_file: Any) -> bytes:
        # 优先尝试写入 BytesIO（如果 SDK 支持 file-like）
        buf = io.BytesIO()
        try:
            video_file.save(buf)
            return buf.getvalue()
        except Exception:
            pass

        # 回退：保存到临时文件后读取
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
                tmp_path = tmp.name
            video_file.save(tmp_path)
            with open(tmp_path, "rb") as f:
                return f.read()
        finally:
            if tmp_path:
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    async def generate_videos(
        self,
        *,
        model: str,
        prompt: str,
        negative_prompt: Optional[str] = None,
        duration_seconds: Optional[int] = None,
        aspect_ratio: Optional[str] = None,
        resolution: Optional[str] = None,
        person_generation: Optional[str] = None,
        first_frame: Optional[Any] = None,
        last_frame: Optional[Any] = None,
        reference_images: Optional[List[Any]] = None,
    ) -> str:
        def _sync() -> str:
            client = self._client()
            _, types = self._import_sdk()

            config_kwargs: Dict[str, Any] = {"number_of_videos": 1}
            if negative_prompt:
                config_kwargs["negative_prompt"] = negative_prompt
            if duration_seconds is not None:
                config_kwargs["duration_seconds"] = str(int(duration_seconds))
            if aspect_ratio:
                config_kwargs["aspect_ratio"] = aspect_ratio
            if resolution:
                config_kwargs["resolution"] = resolution
            if person_generation:
                config_kwargs["person_generation"] = person_generation
            if last_frame is not None:
                config_kwargs["last_frame"] = last_frame
            if reference_images:
                config_kwargs["reference_images"] = [
                    types.VideoGenerationReferenceImage(image=img, reference_type="asset") for img in reference_images
                ]

            config = types.GenerateVideosConfig(**config_kwargs)

            kwargs: Dict[str, Any] = {"model": model, "prompt": prompt, "config": config}
            if first_frame is not None:
                kwargs["image"] = first_frame

            try:
                operation = client.models.generate_videos(**kwargs)
            except Exception as e:
                raise GoogleVeoAPIException("Veo generate_videos 调用失败", details={"error": _safe_str(e)})

            op_name = getattr(operation, "name", None)
            if not op_name:
                raise GoogleVeoAPIException("Veo 返回缺少 operation.name", details={"operation": _safe_str(operation)})
            return str(op_name)

        return await anyio.to_thread.run_sync(_sync)

    async def extend_videos(
        self,
        *,
        source_operation_name: str,
        model: str,
        prompt: str,
        negative_prompt: Optional[str] = None,
        person_generation: Optional[str] = None,
    ) -> str:
        def _sync() -> str:
            client = self._client()
            _, types = self._import_sdk()

            try:
                # 按照官方文档，需要先构造 GenerateVideosOperation 对象
                operation = types.GenerateVideosOperation(name=source_operation_name)
                src_op = client.operations.get(operation)
            except Exception as e:
                raise GoogleVeoAPIException("获取源 operation 失败", details={"error": _safe_str(e)})

            done = bool(getattr(src_op, "done", False))
            if not done:
                raise GoogleVeoAPIException("源 operation 尚未完成，无法延长", details={"source_operation_name": source_operation_name})

            src_error = getattr(src_op, "error", None)
            if src_error:
                raise GoogleVeoAPIException("源 operation 失败，无法延长", details={"error": _safe_str(src_error)})

            src_resp = getattr(src_op, "response", None)
            src_videos = getattr(src_resp, "generated_videos", None) if src_resp is not None else None
            if not src_videos or not isinstance(src_videos, (list, tuple)):
                raise GoogleVeoAPIException("源 operation 无生成视频，无法延长", details={"source_operation_name": source_operation_name})

            first = src_videos[0]
            video_obj = getattr(first, "video", None)
            if video_obj is None:
                raise GoogleVeoAPIException("源 operation 缺少 video 句柄，无法延长", details={"source_operation_name": source_operation_name})

            config_kwargs: Dict[str, Any] = {
                "number_of_videos": 1,
                "resolution": "720p",
            }
            if negative_prompt:
                config_kwargs["negative_prompt"] = negative_prompt
            if person_generation:
                config_kwargs["person_generation"] = person_generation
            config = types.GenerateVideosConfig(**config_kwargs)

            try:
                new_op = client.models.generate_videos(
                    model=model,
                    prompt=prompt,
                    video=video_obj,
                    config=config,
                )
            except Exception as e:
                raise GoogleVeoAPIException("Veo extend 调用失败", details={"error": _safe_str(e)})

            op_name = getattr(new_op, "name", None)
            if not op_name:
                raise GoogleVeoAPIException("Veo 返回缺少 operation.name", details={"operation": _safe_str(new_op)})
            return str(op_name)

        return await anyio.to_thread.run_sync(_sync)

    async def get_operation_info(self, *, operation_name: str) -> Dict[str, Any]:
        def _sync() -> Dict[str, Any]:
            client = self._client()
            _, types = self._import_sdk()

            try:
                # 按照官方文档，需要先构造 GenerateVideosOperation 对象
                operation = types.GenerateVideosOperation(name=operation_name)
                op = client.operations.get(operation)
            except Exception as e:
                raise GoogleVeoAPIException("获取 operation 失败", details={"error": _safe_str(e)})

            name = str(getattr(op, "name", operation_name))
            done = bool(getattr(op, "done", False))
            error_obj = getattr(op, "error", None)
            error_message = None
            if error_obj:
                error_message = getattr(error_obj, "message", None) or _safe_str(error_obj)

            has_video = False
            resp = getattr(op, "response", None)
            videos = getattr(resp, "generated_videos", None) if resp is not None else None
            if videos and isinstance(videos, (list, tuple)) and len(videos) > 0:
                first = videos[0]
                has_video = getattr(first, "video", None) is not None

            status = "running"
            if done:
                if error_obj:
                    status = "failed"
                elif has_video:
                    status = "succeeded"
                else:
                    status = "unknown"

            return {
                "name": name,
                "done": done,
                "status": status,
                "error": error_message,
            }

        return await anyio.to_thread.run_sync(_sync)

    async def download_video_bytes(self, *, operation_name: str) -> bytes:
        def _sync() -> bytes:
            client = self._client()
            _, types = self._import_sdk()

            try:
                # 按照官方文档，需要先构造 GenerateVideosOperation 对象
                operation = types.GenerateVideosOperation(name=operation_name)
                op = client.operations.get(operation)
            except Exception as e:
                raise GoogleVeoAPIException("获取 operation 失败", details={"error": _safe_str(e)})

            done = bool(getattr(op, "done", False))
            if not done:
                raise GoogleVeoAPIException("operation 尚未完成，无法下载", details={"operation_name": operation_name})

            error_obj = getattr(op, "error", None)
            if error_obj:
                raise GoogleVeoAPIException("operation 失败，无法下载", details={"error": _safe_str(error_obj)})

            resp = getattr(op, "response", None)
            videos = getattr(resp, "generated_videos", None) if resp is not None else None
            if not videos or not isinstance(videos, (list, tuple)):
                raise GoogleVeoAPIException("operation 无生成视频，无法下载", details={"operation_name": operation_name})

            first = videos[0]
            video_obj = getattr(first, "video", None)
            if video_obj is None:
                raise GoogleVeoAPIException("operation 缺少 video 句柄，无法下载", details={"operation_name": operation_name})

            try:
                client.files.download(file=video_obj)
            except Exception as e:
                raise GoogleVeoAPIException("下载视频失败", details={"error": _safe_str(e)})

            try:
                return self._extract_video_bytes(video_obj)
            except Exception as e:
                raise GoogleVeoAPIException("读取下载后的视频内容失败", details={"error": _safe_str(e)})

        return await anyio.to_thread.run_sync(_sync)


veo_service = VeoService()

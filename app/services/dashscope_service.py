"""
DashScope API服务
封装阿里云DashScope视频生成API调用
"""
import httpx
from typing import Dict, Any, Optional, List

from app.config import settings
from app.utils.exceptions import DashScopeAPIException


class DashScopeService:
    """DashScope API服务类"""

    def __init__(self):
        """初始化HTTP客户端"""
        self.base_url = settings.dashscope_base_url
        self.api_key = settings.dashscope_api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-DashScope-Async": "enable"  # 必须启用异步模式
        }

    async def create_i2v_task(
        self,
        img_url: str,
        prompt: Optional[str] = None,
        model: str = "wan2.6-i2v",
        negative_prompt: Optional[str] = None,
        audio_url: Optional[str] = None,
        resolution: str = "1080P",
        duration: int = 5,
        prompt_extend: bool = True,
        shot_type: Optional[str] = "single",
        audio: bool = True,
        watermark: bool = False,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        创建图生视频任务

        Args:
            img_url: 图片URL（必选）
            prompt: 文本描述（可选）
            model: 模型名称
            negative_prompt: 反向提示词
            audio_url: 自定义音频URL（优先级高于audio参数）
            resolution: 分辨率
            duration: 时长
            prompt_extend: 是否智能改写prompt
            shot_type: 镜头类型（仅在prompt_extend=true时生效）
            audio: 是否自动配音（audio_url优先级更高）
            watermark: 是否添加水印
            seed: 随机种子

        Returns:
            Dict: API响应数据

        Raises:
            DashScopeAPIException: API调用失败
        """
        url = f"{self.base_url}/api/v1/services/aigc/video-generation/video-synthesis"

        # 构建input对象
        input_data: Dict[str, Any] = {
            "img_url": img_url
        }

        # prompt是可选的
        if prompt:
            input_data["prompt"] = prompt

        # 添加可选输入参数
        if negative_prompt:
            input_data["negative_prompt"] = negative_prompt
        if audio_url:
            input_data["audio_url"] = audio_url

        # 构建parameters对象
        parameters: Dict[str, Any] = {
            "resolution": resolution,
            "duration": duration,
            "prompt_extend": prompt_extend,
            "watermark": watermark
        }

        # audio参数：如果没有audio_url，才使用audio参数
        if not audio_url:
            parameters["audio"] = audio

        # shot_type只在prompt_extend为true时添加
        if prompt_extend and shot_type:
            parameters["shot_type"] = shot_type

        # seed参数
        if seed is not None:
            parameters["seed"] = seed

        payload: Dict[str, Any] = {
            "model": model,
            "input": input_data,
            "parameters": parameters
        }

        return await self._make_request("POST", url, json=payload)

    async def create_t2v_task(
        self,
        prompt: str,
        model: str = "wan2.6-t2v",
        negative_prompt: Optional[str] = None,
        audio_url: Optional[str] = None,
        size: str = "1920*1080",
        duration: int = 5,
        prompt_extend: bool = True,
        shot_type: Optional[str] = "single",
        audio: bool = True,
        watermark: bool = False,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        创建文生视频任务

        Args:
            prompt: 文本描述（必选）
            model: 模型名称
            negative_prompt: 反向提示词
            audio_url: 自定义音频URL（优先级高于audio参数）
            size: 分辨率
            duration: 时长
            prompt_extend: 是否智能改写prompt
            shot_type: 镜头类型（仅在prompt_extend=true时生效）
            audio: 是否自动配音（audio_url优先级更高）
            watermark: 是否添加水印
            seed: 随机种子

        Returns:
            Dict: API响应数据

        Raises:
            DashScopeAPIException: API调用失败
        """
        url = f"{self.base_url}/api/v1/services/aigc/video-generation/video-synthesis"

        # 构建input对象
        input_data: Dict[str, Any] = {
            "prompt": prompt
        }

        # 添加可选输入参数
        if negative_prompt:
            input_data["negative_prompt"] = negative_prompt
        if audio_url:
            input_data["audio_url"] = audio_url

        # 构建parameters对象
        parameters: Dict[str, Any] = {
            "size": size,
            "duration": duration,
            "prompt_extend": prompt_extend,
            "watermark": watermark
        }

        # audio参数：如果没有audio_url，才使用audio参数
        if not audio_url:
            parameters["audio"] = audio

        # shot_type只在prompt_extend为true时添加
        if prompt_extend and shot_type:
            parameters["shot_type"] = shot_type

        # seed参数
        if seed is not None:
            parameters["seed"] = seed

        payload: Dict[str, Any] = {
            "model": model,
            "input": input_data,
            "parameters": parameters
        }

        return await self._make_request("POST", url, json=payload)

    async def create_r2v_task(
        self,
        prompt: str,
        reference_video_urls: List[str],
        model: str = "wan2.6-r2v",
        negative_prompt: Optional[str] = None,
        size: str = "1920*1080",
        duration: int = 5,
        shot_type: Optional[str] = "single",
        audio: bool = True,
        watermark: bool = False,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        创建参考生视频任务

        Args:
            prompt: 文本描述（必选）
            reference_video_urls: 参考视频URL列表（最多3个）
            model: 模型名称
            negative_prompt: 反向提示词
            size: 分辨率
            duration: 时长
            shot_type: 镜头类型
            audio: 是否自动配音
            watermark: 是否添加水印
            seed: 随机种子

        Returns:
            Dict: API响应数据

        Raises:
            DashScopeAPIException: API调用失败
        """
        url = f"{self.base_url}/api/v1/services/aigc/video-generation/video-synthesis"

        # 构建input对象
        input_data: Dict[str, Any] = {
            "prompt": prompt,
            "reference_video_urls": reference_video_urls
        }

        # 添加可选输入参数
        if negative_prompt:
            input_data["negative_prompt"] = negative_prompt

        # 构建parameters对象
        parameters: Dict[str, Any] = {
            "size": size,
            "duration": duration,
            "audio": audio,
            "watermark": watermark
        }

        # shot_type参数
        if shot_type:
            parameters["shot_type"] = shot_type

        # seed参数
        if seed is not None:
            parameters["seed"] = seed

        payload: Dict[str, Any] = {
            "model": model,
            "input": input_data,
            "parameters": parameters
        }

        return await self._make_request("POST", url, json=payload)

    async def query_task(self, task_id: str) -> Dict[str, Any]:
        """
        查询任务状态

        Args:
            task_id: 任务ID

        Returns:
            Dict: 任务状态信息

        Raises:
            DashScopeAPIException: API调用失败
        """
        url = f"{self.base_url}/api/v1/tasks/{task_id}"

        # 查询请求不需要 X-DashScope-Async 头
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        return await self._make_request("GET", url, headers=headers)

    async def _make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        发送HTTP请求

        Args:
            method: 请求方法
            url: 请求URL
            headers: 请求头
            **kwargs: 其他请求参数

        Returns:
            Dict: 响应数据

        Raises:
            DashScopeAPIException: 请求失败
        """
        if headers is None:
            headers = self.headers

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.request(method, url, headers=headers, **kwargs)

                # 尝试解析JSON响应
                try:
                    response_data = response.json()
                except Exception:
                    raise DashScopeAPIException(
                        f"API响应格式错误，状态码: {response.status_code}",
                        details={"response_text": response.text}
                    )

                # 检查HTTP状态码
                if response.status_code not in [200, 201]:
                    error_msg = response_data.get("message", "未知错误")
                    error_code = response_data.get("code", "UNKNOWN")
                    raise DashScopeAPIException(
                        f"DashScope API调用失败: {error_msg}",
                        details={
                            "status_code": response.status_code,
                            "error_code": error_code,
                            "response": response_data
                        }
                    )

                return response_data

        except httpx.HTTPError as e:
            raise DashScopeAPIException(f"HTTP请求失败: {str(e)}")
        except DashScopeAPIException:
            raise
        except Exception as e:
            raise DashScopeAPIException(f"请求异常: {str(e)}")


# 全局DashScope服务实例
dashscope_service = DashScopeService()

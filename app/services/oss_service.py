"""
OSS服务
处理文件上传到阿里云OSS并生成签名URL
"""
import oss2
from datetime import datetime
from typing import Literal
import uuid
import httpx

from app.config import settings
from app.utils.exceptions import OSSUploadException


class OSSService:
    """OSS服务类"""

    def __init__(self):
        """初始化OSS客户端"""
        try:
            auth = oss2.Auth(
                settings.oss_access_key_id,
                settings.oss_access_key_secret
            )
            self.bucket = oss2.Bucket(
                auth,
                settings.oss_endpoint,
                settings.oss_bucket_name
            )
        except Exception as e:
            raise OSSUploadException(f"OSS客户端初始化失败: {str(e)}")

    def _generate_file_path(
        self,
        file_type: Literal["image", "audio", "video", "output_video"],
        file_ext: str
    ) -> str:
        """
        生成文件在OSS中的存储路径

        Args:
            file_type: 文件类型
            file_ext: 文件扩展名

        Returns:
            str: OSS存储路径
        """
        # 根据文件类型选择路径前缀
        path_prefix_map = {
            "image": settings.oss_image_path,
            "audio": settings.oss_audio_path,
            "video": settings.oss_reference_video_path,
            "output_video": settings.oss_output_video_path
        }
        path_prefix = path_prefix_map.get(file_type, "")

        # 生成唯一文件名：日期/UUID.扩展名
        date_str = datetime.now().strftime("%Y%m%d")
        unique_id = uuid.uuid4().hex
        filename = f"{unique_id}.{file_ext}"

        return f"{path_prefix}{date_str}/{filename}"

    async def upload_file(
        self,
        file_content: bytes,
        file_type: Literal["image", "audio", "video", "output_video"],
        file_ext: str
    ) -> tuple[str, str]:
        """
        上传文件到OSS

        Args:
            file_content: 文件内容（字节）
            file_type: 文件类型
            file_ext: 文件扩展名

        Returns:
            tuple[str, str]: (OSS文件路径, 签名URL)

        Raises:
            OSSUploadException: 上传失败
        """
        try:
            # 生成文件路径
            file_path = self._generate_file_path(file_type, file_ext)

            # 上传到OSS
            result = self.bucket.put_object(file_path, file_content)

            if result.status != 200:
                raise OSSUploadException(f"OSS上传失败，状态码: {result.status}")

            # 生成签名URL
            signed_url = self.generate_signed_url(file_path)

            return file_path, signed_url

        except oss2.exceptions.OssError as e:
            raise OSSUploadException(f"OSS上传失败: {str(e)}")
        except Exception as e:
            raise OSSUploadException(f"文件上传异常: {str(e)}")

    def generate_signed_url(self, file_path: str) -> str:
        """
        生成签名URL

        Args:
            file_path: 文件在OSS中的路径

        Returns:
            str: 签名后的公网访问URL

        Raises:
            OSSUploadException: 生成失败
        """
        try:
            # 生成有效期为24小时的签名URL
            signed_url = self.bucket.sign_url(
                'GET',
                file_path,
                settings.oss_url_expiration
            )
            return signed_url
        except Exception as e:
            raise OSSUploadException(f"生成签名URL失败: {str(e)}")

    async def download_and_upload(self, source_url: str, file_type: Literal["output_video"]) -> tuple[str, str]:
        """
        从源URL下载文件并上传到OSS

        Args:
            source_url: 源文件URL
            file_type: 文件类型

        Returns:
            tuple[str, str]: (OSS文件路径, 签名URL)

        Raises:
            OSSUploadException: 下载或上传失败
        """
        try:
            # 异步下载文件
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.get(source_url)
                response.raise_for_status()
                file_content = response.content

            # 从URL中提取文件扩展名
            file_ext = source_url.split(".")[-1].split("?")[0]
            if not file_ext:
                file_ext = "mp4"  # 默认mp4格式

            # 上传到OSS
            return await self.upload_file(file_content, file_type, file_ext)

        except httpx.HTTPError as e:
            raise OSSUploadException(f"文件下载失败: {str(e)}")
        except Exception as e:
            raise OSSUploadException(f"文件转存失败: {str(e)}")


# 全局OSS服务实例
oss_service = OSSService()

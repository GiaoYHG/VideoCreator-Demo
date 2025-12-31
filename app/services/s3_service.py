"""
S3服务
处理文件上传到AWS S3并生成签名URL
"""
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from datetime import datetime
from typing import Literal
import uuid
import httpx

from app.config import settings
from app.utils.exceptions import S3UploadException


class S3Service:
    """S3服务类"""

    def __init__(self):
        """初始化S3客户端"""
        try:
            # 配置S3客户端
            client_config = {
                'aws_access_key_id': settings.s3_access_key_id,
                'aws_secret_access_key': settings.s3_secret_access_key,
                'region_name': settings.s3_region,
            }

            # 如果配置了自定义endpoint（用于S3兼容服务）
            if settings.s3_endpoint_url:
                client_config['endpoint_url'] = settings.s3_endpoint_url

            self.s3_client = boto3.client('s3', **client_config)
            self.bucket_name = settings.s3_bucket_name

            # 测试连接
            self.s3_client.head_bucket(Bucket=self.bucket_name)

        except (ClientError, BotoCoreError) as e:
            raise S3UploadException(f"S3客户端初始化失败: {str(e)}")
        except Exception as e:
            raise S3UploadException(f"S3客户端初始化异常: {str(e)}")

    def _generate_file_path(
        self,
        file_type: Literal["image", "audio", "video", "output_video"],
        file_ext: str
    ) -> str:
        """
        生成文件在S3中的存储路径

        Args:
            file_type: 文件类型
            file_ext: 文件扩展名

        Returns:
            str: S3存储路径
        """
        # 根据文件类型选择路径前缀
        path_prefix_map = {
            "image": settings.s3_image_path,
            "audio": settings.s3_audio_path,
            "video": settings.s3_reference_video_path,
            "output_video": settings.s3_output_video_path
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
        上传文件到S3

        Args:
            file_content: 文件内容（字节）
            file_type: 文件类型
            file_ext: 文件扩展名

        Returns:
            tuple[str, str]: (S3文件路径, 签名URL)

        Raises:
            S3UploadException: 上传失败
        """
        try:
            # 生成文件路径
            file_path = self._generate_file_path(file_type, file_ext)

            # 确定Content-Type
            content_type_map = {
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'gif': 'image/gif',
                'webp': 'image/webp',
                'mp3': 'audio/mpeg',
                'wav': 'audio/wav',
                'mp4': 'video/mp4',
                'avi': 'video/x-msvideo',
                'mov': 'video/quicktime',
            }
            content_type = content_type_map.get(file_ext.lower(), 'application/octet-stream')

            # 上传到S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_path,
                Body=file_content,
                ContentType=content_type
            )

            # 生成签名URL
            signed_url = self.generate_signed_url(file_path)

            return file_path, signed_url

        except (ClientError, BotoCoreError) as e:
            raise S3UploadException(f"S3上传失败: {str(e)}")
        except Exception as e:
            raise S3UploadException(f"文件上传异常: {str(e)}")

    def generate_signed_url(self, file_path: str) -> str:
        """
        生成签名URL

        Args:
            file_path: 文件在S3中的路径

        Returns:
            str: 签名后的公网访问URL

        Raises:
            S3UploadException: 生成失败
        """
        try:
            # 生成有效期为指定时间的签名URL
            signed_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_path
                },
                ExpiresIn=settings.s3_url_expiration
            )
            return signed_url
        except (ClientError, BotoCoreError) as e:
            raise S3UploadException(f"生成签名URL失败: {str(e)}")
        except Exception as e:
            raise S3UploadException(f"生成签名URL异常: {str(e)}")

    async def download_and_upload(self, source_url: str, file_type: Literal["output_video"]) -> tuple[str, str]:
        """
        从源URL下载文件并上传到S3

        Args:
            source_url: 源文件URL
            file_type: 文件类型

        Returns:
            tuple[str, str]: (S3文件路径, 签名URL)

        Raises:
            S3UploadException: 下载或上传失败
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

            # 上传到S3
            return await self.upload_file(file_content, file_type, file_ext)

        except httpx.HTTPError as e:
            raise S3UploadException(f"文件下载失败: {str(e)}")
        except Exception as e:
            raise S3UploadException(f"文件转存失败: {str(e)}")


# 全局 S3 服务实例
s3_service = S3Service()

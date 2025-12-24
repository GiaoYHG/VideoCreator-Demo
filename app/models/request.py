"""
请求模型
定义API接口的请求数据结构
"""
from typing import Optional, Literal
from pydantic import BaseModel, Field


class I2VRequest(BaseModel):
    """图生视频请求模型"""

    prompt: Optional[str] = Field(
        None,
        max_length=1500,
        description="视频描述文本，最长1500字符。wan2.6/wan2.5支持1500字符，wan2.2及以下支持800字符"
    )
    negative_prompt: Optional[str] = Field(
        None,
        max_length=500,
        description="反向提示词，用于描述不希望出现的内容，最长500字符"
    )
    model: str = Field(
        default="wan2.6-i2v",
        description="模型名称",
        examples=["wan2.6-i2v", "wan2.5-i2v-preview", "wan2.2-i2v-plus", "wan2.2-i2v-flash"]
    )
    resolution: Literal["480P", "720P", "1080P"] = Field(
        default="1080P",
        description="视频分辨率档位。wan2.6支持720P/1080P，wan2.5支持480P/720P/1080P"
    )
    duration: int = Field(
        default=5,
        ge=3,
        le=15,
        description="视频时长（秒）。wan2.6支持5/10/15秒，wan2.5支持5/10秒，wan2.1-turbo支持3/4/5秒"
    )
    prompt_extend: bool = Field(
        default=True,
        description="是否开启prompt智能改写，开启后会提升短prompt的生成效果"
    )
    shot_type: Optional[Literal["single", "multi"]] = Field(
        default="single",
        description="镜头类型：single(单镜头)/multi(多镜头)。仅wan2.6支持，且仅在prompt_extend=true时生效"
    )
    audio: bool = Field(
        default=True,
        description="是否自动为视频添加音频。仅wan2.6/wan2.5支持。优先级：audio_url > audio"
    )
    watermark: bool = Field(
        default=False,
        description="是否在视频右下角添加'AI生成'水印"
    )
    seed: Optional[int] = Field(
        None,
        ge=0,
        le=2147483647,
        description="随机种子，取值范围[0, 2147483647]，用于提升结果可复现性"
    )


class T2VRequest(BaseModel):
    """文生视频请求模型"""

    prompt: str = Field(
        ...,
        max_length=1500,
        description="视频描述文本，最长1500字符。wan2.6/wan2.5支持1500字符，wan2.2及以下支持800字符"
    )
    negative_prompt: Optional[str] = Field(
        None,
        max_length=500,
        description="反向提示词，用于描述不希望出现的内容，最长500字符"
    )
    model: str = Field(
        default="wan2.6-t2v",
        description="模型名称",
        examples=["wan2.6-t2v", "wan2.5-t2v-preview", "wan2.2-t2v-plus", "wan2.1-t2v-turbo"]
    )
    size: str = Field(
        default="1920*1080",
        description="视频分辨率，格式: 宽*高（必须是具体数值，如1280*720，不能是1:1或480P）。支持480P/720P/1080P档位的多种宽高比",
        examples=["1920*1080", "1280*720", "720*1280", "1440*1440", "832*480"]
    )
    duration: int = Field(
        default=5,
        ge=3,
        le=15,
        description="视频时长（秒）。wan2.6-t2v支持5/10/15秒，wan2.5支持5/10秒，wan2.2/wan2.1系列固定5秒"
    )
    prompt_extend: bool = Field(
        default=True,
        description="是否开启prompt智能改写，开启后会提升短prompt的生成效果，但会增加耗时"
    )
    shot_type: Optional[Literal["single", "multi"]] = Field(
        default="single",
        description="镜头类型：single(单镜头)/multi(多镜头)。仅wan2.6-t2v支持，且仅在prompt_extend=true时生效。优先级：shot_type > prompt"
    )
    audio: bool = Field(
        default=True,
        description="是否自动为视频添加音频。仅wan2.6-t2v/wan2.5-t2v-preview支持。优先级：audio_url > audio"
    )
    watermark: bool = Field(
        default=False,
        description="是否在视频右下角添加'AI生成'水印"
    )
    seed: Optional[int] = Field(
        None,
        ge=0,
        le=2147483647,
        description="随机种子，取值范围[0, 2147483647]，用于提升结果可复现性"
    )


class R2VRequest(BaseModel):
    """参考生视频请求模型"""

    prompt: str = Field(
        ...,
        max_length=1500,
        description="视频描述文本，最长1500字符。通过character1、character2引用参考角色"
    )
    negative_prompt: Optional[str] = Field(
        None,
        max_length=500,
        description="反向提示词，用于描述不希望出现的内容，最长500字符"
    )
    model: str = Field(
        default="wan2.6-r2v",
        description="模型名称",
        examples=["wan2.6-r2v"]
    )
    size: str = Field(
        default="1920*1080",
        description="视频分辨率，格式: 宽*高。支持720P和1080P档位的多种宽高比",
        examples=["1920*1080", "1280*720", "720*1280", "1440*1440"]
    )
    duration: int = Field(
        default=5,
        description="视频时长（秒）。wan2.6-r2v仅支持5或10秒"
    )
    shot_type: Optional[Literal["single", "multi"]] = Field(
        default="single",
        description="镜头类型：single(单镜头)/multi(多镜头)。优先级：shot_type > prompt"
    )
    audio: bool = Field(
        default=True,
        description="是否自动为视频添加音频（提取参考视频音色）"
    )
    watermark: bool = Field(
        default=False,
        description="是否在视频右下角添加'AI生成'水印"
    )
    seed: Optional[int] = Field(
        None,
        ge=0,
        le=2147483647,
        description="随机种子，取值范围[0, 2147483647]，用于提升结果可复现性"
    )

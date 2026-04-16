"""LLM工厂类"""
from typing import Optional

from ..config import get_config
from .base import LLMBase
from .minimax import MinimaxAdapter
from .glm import GLMAdapter


class LLMFactory:
    """LLM适配器工厂"""

    _adapters: dict[str, LLMBase] = {}

    @classmethod
    def get_adapter(cls, provider: Optional[str] = None) -> LLMBase:
        """
        获取LLM适配器实例

        Args:
            provider: 提供商名称，如不指定则使用配置文件中的默认值

        Returns:
            LLMBase适配器实例
        """
        if provider is None:
            provider = get_config().default_provider

        if provider in cls._adapters:
            return cls._adapters[provider]

        config = get_config()
        provider_config = config.providers.get(provider)

        if provider_config is None:
            raise ValueError(f"未知的LLM提供商: {provider}")

        if provider == "minimax":
            adapter = MinimaxAdapter(
                group_id=provider_config.group_id,
                api_key=provider_config.api_key,
                model=provider_config.model,
                base_url=provider_config.base_url,
            )
        elif provider == "glm":
            adapter = GLMAdapter(
                api_key=provider_config.api_key,
                model=provider_config.model,
                base_url=provider_config.base_url,
            )
        else:
            raise ValueError(f"不支持的LLM提供商: {provider}")

        cls._adapters[provider] = adapter
        return adapter

    @classmethod
    def clear_cache(cls):
        """清除适配器缓存"""
        cls._adapters.clear()

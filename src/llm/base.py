"""LLM适配器基类"""
from abc import ABC, abstractmethod
from typing import Optional


class LLMBase(ABC):
    """大模型适配器基类"""

    @abstractmethod
    def complete(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        调用大模型完成文本生成

        Args:
            prompt: 用户输入提示
            system_prompt: 系统提示（可选）

        Returns:
            模型生成的文本
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """提供商名称"""
        pass

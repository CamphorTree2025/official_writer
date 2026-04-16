"""智谱GLM大模型适配器"""
from typing import Optional

import httpx

from .base import LLMBase


class GLMAdapter(LLMBase):
    """智谱GLM大模型适配器"""

    def __init__(
        self,
        api_key: str,
        model: str = "glm-4",
        base_url: str = "https://open.bigmodel.cn/api/paas/v4",
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )

    @property
    def provider_name(self) -> str:
        return "glm"

    def complete(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """调用智谱GLM API"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
        }

        response = self._client.post(
            f"{self.base_url}/chat/completions",
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def __del__(self):
        if hasattr(self, "_client"):
            self._client.close()

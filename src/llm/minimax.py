"""Minimax大模型适配器"""
from typing import Optional

import httpx

from .base import LLMBase


class MinimaxAdapter(LLMBase):
    """Minimax大模型适配器"""

    def __init__(
        self,
        group_id: str,
        api_key: str,
        model: str = "abab6.5s",
        base_url: str = "https://api.minimaxi.com/v1",
    ):
        self.group_id = group_id
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "GroupId": self.group_id,
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )

    @property
    def provider_name(self) -> str:
        return "minimax"

    def complete(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """调用Minimax API"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
        }

        print(f"Minimax API request: {self.base_url}/text/chatcompletion_v2")
        print(f"Model: {self.model}")
        response = self._client.post(
            f"{self.base_url}/text/chatcompletion_v2",
            json=payload,
        )
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text[:1000]}")

        response.raise_for_status()
        data = response.json()

        if not data.get("choices"):
            raise ValueError(f"Minimax API返回异常: {data}")

        return data["choices"][0]["message"]["content"]

    def __del__(self):
        if hasattr(self, "_client"):
            self._client.close()

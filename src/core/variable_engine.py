"""变量替换引擎"""
from pathlib import Path
from typing import Dict, List, Optional

from ..llm.base import LLMBase


class VariableEngine:
    """变量替换引擎，通过LLM理解用户输入并填充模板变量"""

    SYSTEM_PROMPT = """你是一个公文写作助手。用户会提供一个模板和需要填写的内容主题。
请严格按照模板的格式和语义要求，填写每个占位符的内容。

要求：
1. 严格遵循模板的格式要求
2. 内容要符合公文写作规范
3. 语言要正式、规范
4. 只输出填充后的内容，不要额外的解释
"""

    def __init__(self, llm_adapter: LLMBase):
        self.llm = llm_adapter

    def fill_template(
        self,
        template_text: str,
        variables: List[str],
        user_input: str,
        context: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """
        填充模板变量

        Args:
            template_text: 模板纯文本内容
            variables: 变量名列表
            user_input: 用户输入的文字描述
            context: 额外的上下文信息

        Returns:
            {变量名: 填充内容} 的字典
        """
        context = context or {}

        prompt = self._build_prompt(template_text, variables, user_input, context)
        response = self.llm.complete(prompt, system_prompt=self.SYSTEM_PROMPT)

        return self._parse_filled_content(response, variables)

    def _build_prompt(
        self,
        template_text: str,
        variables: List[str],
        user_input: str,
        context: Dict[str, str],
    ) -> str:
        """构建提示词"""
        var_list = "\n".join([f"- {{{v}}}" for v in variables])

        prompt = f"""请根据以下信息填充公文模板：

## 用户输入
{user_input}

## 模板中的变量
{var_list}

## 完整模板内容
{template_text}
"""

        if context:
            context_str = "\n".join([f"- {k}: {v}" for k, v in context.items()])
            prompt += f"\n## 额外上下文\n{context_str}\n"

        prompt += "\n请为每个变量生成填充内容，格式如下：\n"
        for var in variables:
            prompt += f"[{var}]: 这里填入{var}的内容\n"

        return prompt

    def _parse_filled_content(
        self, response: str, variables: List[str]
    ) -> Dict[str, str]:
        """解析LLM返回的内容"""
        result = {}
        lines = response.strip().split("\n")

        for var in variables:
            var_patterns = [
                f"[{var}]",
                f"{var}:",
                f"【{var}】",
                f"「{var}」",
            ]
            for line in lines:
                for pattern in var_patterns:
                    if pattern in line:
                        content = line.split(pattern)[-1].strip()
                        content = content.strip("：:").strip()
                        result[var] = content
                        break
                if var in result:
                    break

        return result

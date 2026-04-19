"""变量替换引擎"""
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum

from ..llm.base import LLMBase


class FillMode(Enum):
    """填充模式"""
    STRICT = "strict"       # 严格模式：只从输入中提取，不修改原文，未识别则标记
    POLISH = "polish"       # AI润色模式：识别+润色，缺失内容由AI补充


class VariableEngine:
    """变量替换引擎，通过LLM理解用户输入并填充模板变量"""

    SYSTEM_PROMPT_STRICT = """你是一个公文信息提取助手。你的任务是从用户输入的文本中，严格提取与模板变量对应的内容。

严格要求：
1. 只从用户输入中提取已明确提及的信息，不要自行编造或推测任何内容
2. 提取的内容必须与用户输入原文保持完全一致，不做任何修改、润色或增删
3. 如果用户输入中没有提及某个变量对应的信息，必须输出 [未识别]
4. 只输出变量填充结果，不要输出任何额外的解释或说明
5. 输出格式严格为：[变量名]: 填充内容

示例：
用户输入：关于召开安全生产工作会议的通知，会议时间为12月15日
模板变量：会议名称, 发文机关, 日期, 正文内容
正确输出：
[会议名称]: 安全生产工作会议
[发文机关]: [未识别]
[日期]: 12月15日
[正文内容]: [未识别]
"""

    SYSTEM_PROMPT_POLISH = """你是一个公文写作助手。用户会提供一个模板和需要填写的内容描述。
请根据用户描述，填写每个模板变量的内容。

要求：
1. 如果用户描述中明确提及了某个变量的内容，基于该内容进行润色，使其符合公文写作规范
2. 如果用户描述中未提及某个变量的内容，根据上下文和公文规范合理补充
3. 语言要正式、规范，符合公文写作要求
4. 只输出变量填充结果，不要输出任何额外的解释或说明
5. 输出格式严格为：[变量名]: 填充内容
"""

    def __init__(self, llm_adapter: LLMBase):
        self.llm = llm_adapter

    def fill_template(
        self,
        template_text: str,
        variables: List[str],
        user_input: str,
        context: Optional[Dict[str, str]] = None,
        mode: str = "polish",
    ) -> Tuple[Dict[str, str], Dict[str, str]]:
        """
        填充模板变量

        Args:
            template_text: 模板纯文本内容
            variables: 变量名列表
            user_input: 用户输入的文字描述
            context: 额外的上下文信息
            mode: 填充模式 - "strict"(严格提取) 或 "polish"(AI润色)

        Returns:
            (填充结果字典, 变量来源字典)
            填充结果: {变量名: 填充内容}
            变量来源: {变量名: "extracted"/"polished"/"manual"}
        """
        context = context or {}
        fill_mode = FillMode(mode)

        if fill_mode == FillMode.STRICT:
            prompt = self._build_strict_prompt(template_text, variables, user_input, context)
            system_prompt = self.SYSTEM_PROMPT_STRICT
        else:
            prompt = self._build_polish_prompt(template_text, variables, user_input, context)
            system_prompt = self.SYSTEM_PROMPT_POLISH

        response = self.llm.complete(prompt, system_prompt=system_prompt)
        parsed = self._parse_filled_content(response, variables)

        # 按模板变量顺序构建返回结果，确保前端显示顺序与模板一致
        filled_content = {}
        sources = {}
        for var in variables:
            value = parsed.get(var, "")
            if fill_mode == FillMode.STRICT:
                if not value or value == "[未识别]" or value.strip() == "":
                    filled_content[var] = ""
                    sources[var] = "manual"  # 需要手动填写
                else:
                    filled_content[var] = value
                    sources[var] = "extracted"  # 从输入中提取
            else:
                if not value or value.strip() == "":
                    filled_content[var] = ""
                    sources[var] = "manual"
                else:
                    filled_content[var] = value
                    sources[var] = "polished"  # AI润色/补充

        return filled_content, sources

    def _build_strict_prompt(
        self,
        template_text: str,
        variables: List[str],
        user_input: str,
        context: Dict[str, str],
    ) -> str:
        """构建严格模式的提示词"""
        var_list = "\n".join([f"- {{{v}}}" for v in variables])

        prompt = f"""请从以下用户输入中严格提取信息，填入模板变量。

## 用户输入
{user_input}

## 模板中的变量
{var_list}

## 完整模板内容（供参考变量语义）
{template_text}
"""

        if context:
            context_str = "\n".join([f"- {k}: {v}" for k, v in context.items()])
            prompt += f"\n## 额外上下文\n{context_str}\n"

        prompt += """
重要提醒：
- 提取的内容必须与用户输入原文完全一致，不可修改任何文字
- 如果用户输入中没有提及某个变量对应的信息，必须输出 [未识别]
- 严格按照以下格式输出，每个变量一行：
"""
        for var in variables:
            prompt += f"[{var}]: \n"

        return prompt

    def _build_polish_prompt(
        self,
        template_text: str,
        variables: List[str],
        user_input: str,
        context: Dict[str, str],
    ) -> str:
        """构建润色模式的提示词"""
        var_list = "\n".join([f"- {{{v}}}" for v in variables])

        prompt = f"""请根据以下信息填充公文模板变量：

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

        prompt += """
请为每个变量生成填充内容：
- 如果用户描述中已有该信息，基于原文润色使其符合公文规范
- 如果用户描述中未提及，根据上下文合理补充
- 严格按照以下格式输出，每个变量一行：
"""
        for var in variables:
            prompt += f"[{var}]: \n"

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
                        # 保留 [未识别] 标记
                        result[var] = content
                        break
                if var in result:
                    break

        return result

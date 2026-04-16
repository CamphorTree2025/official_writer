"""格式校验模块"""
from typing import Dict, List, Set


class FormatValidator:
    """校验生成内容是否符合格式要求"""

    def __init__(self, required_variables: List[str]):
        self.required_variables = required_variables
        self.filled_variables: Set[str] = set()

    def validate(self, filled_content: Dict[str, str]) -> tuple[bool, List[str]]:
        """
        校验填充结果

        Args:
            filled_content: {变量名: 内容}

        Returns:
            (是否通过校验, 错误信息列表)
        """
        errors = []

        missing_vars = set(self.required_variables) - set(filled_content.keys())
        if missing_vars:
            errors.append(f"缺少以下变量: {', '.join(missing_vars)}")

        for var, content in filled_content.items():
            if not content or not content.strip():
                errors.append(f"变量 {var} 填充内容为空")

        return len(errors) == 0, errors

    def mark_filled(self, var_name: str):
        """标记变量已填充"""
        self.filled_variables.add(var_name)

    def get_missing_variables(self) -> Set[str]:
        """获取未填充的变量"""
        return set(self.required_variables) - self.filled_variables

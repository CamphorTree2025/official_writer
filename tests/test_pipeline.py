"""简单测试脚本"""
from pathlib import Path
from src.config import load_config
from src.core.template_parser import TemplateParser
from src.llm.factory import LLMFactory
from src.core.variable_engine import VariableEngine
from src.output.docx_generator import DocxGenerator

def test_pipeline():
    """测试完整流程"""
    # 加载配置
    load_config()

    # 测试LLM工厂
    llm = LLMFactory.get_adapter("minimax")
    print(f"LLM Provider: {llm.provider_name}")

    # 测试变量引擎
    engine = VariableEngine(llm)
    test_template = "关于召开{{会议名称}}的通知\n\n各位同事：\n{{正文}}\n\n{{落款}}"
    test_variables = ["会议名称", "正文", "落款"]
    test_input = "召开2024年度安全生产工作会议"

    print(f"测试模板: {test_template}")
    print(f"测试输入: {test_input}")

    result = engine.fill_template(test_template, test_variables, test_input)
    print(f"填充结果: {result}")

if __name__ == "__main__":
    test_pipeline()

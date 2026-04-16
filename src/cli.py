"""命令行入口"""
import sys
from pathlib import Path

import click

from .config import load_config
from .core.template_parser import TemplateParser
from .core.variable_engine import VariableEngine
from .core.format_validator import FormatValidator
from .llm.factory import LLMFactory
from .output.docx_generator import DocxGenerator


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """公文写作助手 - 基于模板的AI公文生成工具"""
    pass


@cli.command()
@click.option(
    "--template", "-t",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="模板文件路径(.docx)"
)
@click.option(
    "--input", "-i",
    type=str,
    required=True,
    help="用户输入的文字描述"
)
@click.option(
    "--output", "-o",
    type=click.Path(path_type=Path),
    required=True,
    help="输出文件路径(.docx)"
)
@click.option(
    "--model", "-m",
    type=str,
    default=None,
    help="LLM提供商 (minimax/glm)，默认使用配置文件中的默认值"
)
@click.option(
    "--config", "-c",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="配置文件路径"
)
def generate(
    template: Path,
    input: str,
    output: Path,
    model: str | None,
    config: Path | None,
):
    """根据模板生成公文"""
    try:
        if config:
            load_config(str(config))
        else:
            load_config()

        click.echo(f"正在加载模板: {template}")
        parser = TemplateParser()
        template_text, variables = parser.parse(template)

        if not variables:
            click.echo("警告: 模板中未发现变量占位符", err=True)
            variables = []

        click.echo(f"发现 {len(variables)} 个变量: {', '.join(variables)}")

        click.echo(f"正在调用大模型填充变量...")
        llm = LLMFactory.get_adapter(model)
        click.echo(f"使用模型: {llm.provider_name}")

        engine = VariableEngine(llm)
        filled_content = engine.fill_template(template_text, variables, input)

        validator = FormatValidator(variables)
        is_valid, errors = validator.validate(filled_content)
        if not is_valid:
            click.echo("警告: 填充校验未通过:", err=True)
            for error in errors:
                click.echo(f"  - {error}", err=True)

        click.echo(f"正在生成文档: {output}")
        generator = DocxGenerator()
        generator.generate(template, filled_content, output)

        click.echo(click.style("生成成功!", fg="green"))
        click.echo(f"输出文件: {output}")

    except Exception as e:
        click.echo(click.style(f"错误: {e}", fg="red"), err=True)
        sys.exit(1)


@cli.command()
@click.argument("template", type=click.Path(exists=True, path_type=Path))
def info(template: Path):
    """查看模板信息"""
    try:
        load_config()
        parser = TemplateParser()
        template_text, variables = parser.parse(template)

        click.echo(f"模板文件: {template}")
        click.echo(f"变量数量: {len(variables)}")

        if variables:
            click.echo("\n变量列表:")
            for var in variables:
                click.echo(f"  - {{{{{var}}}}}")
        else:
            click.echo("\n未发现变量占位符")

    except Exception as e:
        click.echo(click.style(f"错误: {e}", fg="red"), err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()

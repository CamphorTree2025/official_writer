"""配置管理模块"""
import os
import re
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel


class LLMProviderConfig(BaseModel):
    """LLM提供商配置"""
    api_key: str = ""
    model: str = ""
    base_url: str = ""
    group_id: str = ""  # Minimax专用


class Config(BaseModel):
    """全局配置"""
    default_provider: str
    providers: dict[str, LLMProviderConfig]
    variable_pattern: str = r"{{(.*?)}}"
    default_variables: dict[str, str] = {}


_config: Optional[Config] = None
_config_path: Optional[Path] = None


def _resolve_env_vars(value: str) -> str:
    """解析环境变量引用，如 ${VAR_NAME} -> actual value"""
    pattern = r"\$\{([^}]+)\}"
    matches = re.findall(pattern, value)
    for match in matches:
        env_value = os.environ.get(match, "")
        value = value.replace(f"${{{match}}}", env_value)
    return value


def _process_dict_env_vars(d: dict) -> dict:
    """递归处理字典中的环境变量"""
    result = {}
    for k, v in d.items():
        if isinstance(v, str):
            result[k] = _resolve_env_vars(v)
        elif isinstance(v, dict):
            result[k] = _process_dict_env_vars(v)
        else:
            result[k] = v
    return result


def _find_project_root() -> Path:
    """从当前文件位置向上查找项目根目录"""
    current = Path(__file__).resolve().parent
    for _ in range(10):  # 最多向上10层
        if (current / "config.yaml").exists():
            return current
        current = current.parent
    # 默认返回当前所在目录
    return Path(__file__).resolve().parent.parent


def get_project_root() -> Path:
    """获取项目根目录（供其他模块使用）"""
    return _find_project_root()


def load_config(config_path: Optional[str] = None) -> Config:
    """加载配置文件"""
    global _config, _config_path

    if config_path:
        _config_path = Path(config_path).resolve()
    elif _config_path is None:
        _config_path = _find_project_root() / "config.yaml"

    with open(_config_path, "r", encoding="utf-8") as f:
        raw_config = yaml.safe_load(f)

    config_dict = _process_dict_env_vars(raw_config)

    providers = {}
    for name, provider_data in config_dict.get("llm", {}).get("providers", {}).items():
        providers[name] = LLMProviderConfig(**provider_data)

    _config = Config(
        default_provider=config_dict.get("llm", {}).get("default_provider", "minimax"),
        providers=providers,
        variable_pattern=config_dict.get("template", {}).get("variable_pattern", r"{{(.*?)}}"),
        default_variables=config_dict.get("template", {}).get("default_variables", {}),
    )
    return _config


def get_config() -> Config:
    """获取全局配置（懒加载）"""
    global _config
    if _config is None:
        load_config()
    return _config

"""Flask Web应用"""
import os
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_from_directory, redirect, url_for
from pathlib import Path
import httpx

from ..config import load_config, get_config, Config, get_project_root
from ..core.template_parser import TemplateParser
from ..core.variable_engine import VariableEngine
from ..llm.factory import LLMFactory
from ..output.docx_generator import DocxGenerator


# 历史记录文件路径
def _get_history_path():
    return get_project_root() / "outputs" / ".history.json"


def _load_history():
    """加载生成历史"""
    path = _get_history_path()
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def _save_history(history):
    """保存生成历史"""
    path = _get_history_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def create_app():
    """创建Flask应用"""
    # 获取项目根目录
    project_root = get_project_root()
    template_folder = project_root / "templates"
    static_folder = project_root / "src" / "gui" / "static"

    app = Flask(
        __name__,
        template_folder=str(template_folder),
        static_folder=str(static_folder)
    )

    # 文件上传配置
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 最大16MB
    ALLOWED_EXTENSIONS = {"docx"}

    def allowed_file(filename):
        return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

    # 确保模板和输出目录存在
    (project_root / "templates").mkdir(exist_ok=True)
    (project_root / "outputs").mkdir(exist_ok=True)

    # ===== 页面路由 =====

    @app.route("/")
    def index():
        """首页 - Dashboard"""
        return render_template("index.html")

    @app.route("/config")
    def config_page():
        """API配置页面"""
        return render_template("config.html")

    @app.route("/templates")
    def templates_page():
        """模板管理页面"""
        return render_template("templates.html")

    @app.route("/generate")
    def generate_page():
        """公文生成页面"""
        return render_template("generate.html")

    # ===== API 路由 =====

    @app.route("/api/config", methods=["GET"])
    def get_config_api():
        """获取当前配置"""
        try:
            config = get_config()
            providers = []
            for name, provider in config.providers.items():
                providers.append({
                    "name": name,
                    "model": provider.model,
                    "base_url": provider.base_url,
                    "api_key": provider.api_key,  # 返回实际key供前端显示
                    "group_id": provider.group_id,
                    "has_key": bool(provider.api_key),
                })
            return jsonify({
                "default_provider": config.default_provider,
                "providers": providers,
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/config", methods=["POST"])
    def save_config_api():
        """保存配置"""
        try:
            data = request.json
            config_path = get_project_root() / "config.yaml"

            import yaml
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)

            if "default_provider" in data:
                config_data["llm"]["default_provider"] = data["default_provider"]

            if "providers" in data:
                # 默认base_url配置
                default_urls = {
                    "minimax": "https://api.minimaxi.com/v1",
                    "glm": "https://open.bigmodel.cn/api/paas/v4",
                    "openai": "https://api.openai.com/v1"
                }
                default_models = {
                    "minimax": "abab6.5s",
                    "glm": "glm-4",
                    "openai": "gpt-4"
                }

                for name, provider_data in data["providers"].items():
                    # 如果提供商不存在则创建
                    if name not in config_data["llm"]["providers"]:
                        config_data["llm"]["providers"][name] = {
                            "api_key": "",
                            "model": default_models.get(name, ""),
                            "base_url": default_urls.get(name, ""),
                            "group_id": ""
                        }
                    # 更新提供商配置
                    if "api_key" in provider_data:
                        config_data["llm"]["providers"][name]["api_key"] = provider_data["api_key"]
                    if "model" in provider_data:
                        config_data["llm"]["providers"][name]["model"] = provider_data["model"]
                    if "group_id" in provider_data:
                        config_data["llm"]["providers"][name]["group_id"] = provider_data["group_id"]
                    if "base_url" in provider_data:
                        config_data["llm"]["providers"][name]["base_url"] = provider_data["base_url"]

            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)

            # 重新加载配置并清除缓存
            load_config(str(config_path))
            from ..llm.factory import LLMFactory
            LLMFactory.clear_cache()

            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/config/provider/<provider_name>", methods=["DELETE"])
    def delete_provider_config(provider_name):
        """删除提供商配置"""
        try:
            config_path = get_project_root() / "config.yaml"

            import yaml
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)

            if provider_name in config_data["llm"]["providers"]:
                del config_data["llm"]["providers"][provider_name]

            # 如果删除的是默认提供商，改成其他的
            if config_data["llm"]["default_provider"] == provider_name:
                providers = list(config_data["llm"]["providers"].keys())
                config_data["llm"]["default_provider"] = providers[0] if providers else "minimax"

            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)

            load_config(str(config_path))
            return jsonify({"success": True, "deleted": provider_name})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/config/test", methods=["POST"])
    def test_provider_config():
        """测试提供商配置是否正确"""
        try:
            data = request.json
            provider_name = data.get("provider")
            group_id = data.get("group_id", "")
            api_key = data.get("api_key", "")
            model = data.get("model", "")
            base_url = data.get("base_url", "")

            # 根据提供商创建临时适配器测试
            from ..llm.minimax import MinimaxAdapter
            from ..llm.glm import GLMAdapter

            if provider_name == "minimax":
                adapter = MinimaxAdapter(
                    group_id=group_id,
                    api_key=api_key,
                    model=model or "abab6.5s",
                    base_url=base_url or "https://api.minimaxi.com/v1"
                )
            elif provider_name == "glm":
                adapter = GLMAdapter(
                    api_key=api_key,
                    model=model or "glm-4",
                    base_url=base_url or "https://open.bigmodel.cn/api/paas/v4"
                )
            else:
                return jsonify({"success": False, "error": f"不支持的提供商: {provider_name}"}), 400

            # 调用API测试
            test_prompt = "请回复'测试成功'，只用这四个字。"
            response = adapter.complete(test_prompt)

            return jsonify({
                "success": True,
                "message": "配置正确，API调用成功！",
                "response": response
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/templates", methods=["GET"])
    def list_templates():
        """列出可用模板"""
        try:
            project_root = get_project_root()
            template_dir = project_root / "templates"
            templates = []
            for f in template_dir.glob("*.docx"):
                # 过滤 macOS 资源分叉文件
                if f.name.startswith("._"):
                    continue
                templates.append({
                    "name": f.name,
                    "path": str(f),
                    "size": f.stat().st_size,
                })
            return jsonify(templates)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/template/preview")
    def preview_template():
        """预览模板内容"""
        try:
            from urllib.parse import unquote
            filename = request.args.get("name", "")
            filename = unquote(filename)
            if not filename:
                return jsonify({"error": "缺少文件名"}), 400

            project_root = get_project_root()
            template_path = project_root / "templates" / filename

            if not template_path.exists():
                return jsonify({"error": f"模板文件不存在: {filename}"}), 400

            parser = TemplateParser()
            preview_data = parser.get_preview(template_path)
            return jsonify(preview_data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/template/<path:filename>")
    def download_template(filename):
        """下载模板文件"""
        project_root = get_project_root()
        return send_from_directory(project_root / "templates", filename, as_attachment=True)

    @app.route("/api/template/delete", methods=["POST"])
    def delete_template():
        """删除模板文件"""
        try:
            from urllib.parse import unquote
            data = request.json
            filename = data.get("name", "")
            filename = unquote(filename)
            if not filename:
                return jsonify({"error": "缺少文件名"}), 400

            project_root = get_project_root()
            template_path = project_root / "templates" / filename

            if not template_path.exists():
                return jsonify({"error": f"模板文件不存在: {filename}"}), 400

            template_path.unlink()
            return jsonify({"success": True, "deleted": filename})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/template/upload", methods=["POST"])
    def upload_template():
        """上传模板文件"""
        try:
            if "file" not in request.files:
                return jsonify({"error": "没有文件"}), 400

            file = request.files["file"]
            if file.filename == "":
                return jsonify({"error": "没有选择文件"}), 400

            if file and allowed_file(file.filename):
                filename = file.filename
                # 确保文件名安全
                if not filename.replace(".", "").replace("_", "").replace("-", "").replace("（", "").replace("）", "").isalnum():
                    import time
                    filename = f"template_{int(time.time())}.docx"

                project_root = get_project_root()
                save_path = project_root / "templates" / filename
                file.save(save_path)
                return jsonify({
                    "success": True,
                    "name": filename,
                    "path": str(save_path),
                })
            else:
                return jsonify({"error": "只支持.docx格式文件"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/template/variables")
    def get_template_variables():
        """获取模板中的变量"""
        try:
            from urllib.parse import unquote

            filename = request.args.get("name", "")
            filename = unquote(filename)

            if not filename:
                return jsonify({"error": "缺少文件名"}), 400

            project_root = get_project_root()
            template_dir = project_root / "templates"
            template_path = template_dir / filename

            if not template_path.exists():
                files = list(template_dir.glob("*.docx"))
                matched = [f for f in files if filename in f.name or f.stem in filename]
                if matched:
                    template_path = matched[0]
                else:
                    return jsonify({
                        "error": "模板文件不存在",
                        "searched": filename,
                        "available": [f.name for f in files]
                    }), 400

            parser = TemplateParser()
            text, variables = parser.parse(template_path)
            return jsonify({
                "variables": variables,
                "text_preview": text[:500] if text else "",
                "found_file": template_path.name
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/preview", methods=["POST"])
    def preview_variables():
        """预览变量填充结果（供用户编辑）"""
        try:
            data = request.json
            template_name = data.get("template_name", "")
            user_input = data.get("input", "")
            model_provider = data.get("model")
            fill_mode = data.get("mode", "polish")  # strict 或 polish

            if not template_name:
                return jsonify({"error": "请选择模板"}), 400

            if not user_input:
                return jsonify({"error": "请输入公文内容描述"}), 400

            if not model_provider:
                return jsonify({"error": "请选择 AI 模型"}), 400

            # 校验填充模式
            if fill_mode not in ("strict", "polish"):
                return jsonify({"error": f"无效的填充模式: {fill_mode}，仅支持 strict 或 polish"}), 400

            project_root = get_project_root()
            template_path = project_root / "templates" / template_name

            if not template_path.exists():
                return jsonify({"error": "模板文件不存在"}), 400

            # 检查提供商是否已配置
            config = get_config()
            provider_config = config.providers.get(model_provider)
            if provider_config is None:
                available = list(config.providers.keys())
                return jsonify({
                    "error": f"未知的LLM提供商: {model_provider}，当前已配置: {', '.join(available) if available else '无'}。请前往 API 配置页面添加。"
                }), 400

            if not provider_config.api_key:
                return jsonify({
                    "error": f"{model_provider} 的 API Key 未配置，请前往 API 配置页面设置"
                }), 400

            # 解析模板
            parser = TemplateParser()
            template_text, variables = parser.parse(template_path)

            if not variables:
                return jsonify({"variables": {}, "sources": {}, "message": "模板中没有变量"})

            # 调用LLM填充变量（支持模式）
            llm = LLMFactory.get_adapter(model_provider)
            engine = VariableEngine(llm)
            filled_content, sources = engine.fill_template(
                template_text, variables, user_input, mode=fill_mode
            )

            return jsonify({
                "variables": filled_content,
                "sources": sources,
                "mode": fill_mode,
            })
        except httpx.TimeoutException:
            return jsonify({"error": "AI 服务响应超时，请稍后重试或换一个模型"}), 504
        except httpx.ConnectError:
            return jsonify({"error": "无法连接 AI 服务，请检查网络连接"}), 502
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            if status_code == 401:
                return jsonify({"error": "API Key 无效或已过期，请前往配置页面检查"}), 401
            elif status_code == 429:
                return jsonify({"error": "AI 服务请求频率过高，请稍后重试"}), 429
            else:
                return jsonify({"error": f"AI 服务返回错误 ({status_code})，请稍后重试"}), 500
        except Exception as e:
            import traceback
            error_msg = str(e)
            # 对常见错误做友好提示
            if "api_key" in error_msg.lower() or "apikey" in error_msg.lower():
                return jsonify({"error": "API Key 无效或已过期，请前往配置页面检查"}), 401
            return jsonify({"error": error_msg, "trace": traceback.format_exc()}), 500

    @app.route("/api/generate", methods=["POST"])
    def generate_doc():
        """生成公文"""
        try:
            data = request.json
            template_name = data.get("template_name", "")
            user_input = data.get("input", "")
            output_name = data.get("output_name", "公文.docx")
            model_provider = data.get("model")
            filled_content = data.get("filled_content", {})

            if not template_name:
                return jsonify({"error": "请选择模板"}), 400

            project_root = get_project_root()
            template_path = project_root / "templates" / template_name
            if not template_path.exists():
                return jsonify({"error": "模板文件不存在"}), 400

            if not filled_content and not user_input:
                return jsonify({"error": "请输入公文内容描述"}), 400

            # 解析模板获取变量列表
            parser = TemplateParser()
            template_text, variables = parser.parse(template_path)

            # 如果没有提供预填充内容，则调用LLM生成
            if not filled_content:
                llm = LLMFactory.get_adapter(model_provider)
                engine = VariableEngine(llm)
                filled_content = engine.fill_template(template_text, variables, user_input)

            # 生成文档
            output_path = project_root / "outputs" / output_name
            generator = DocxGenerator()
            generator.generate(template_path, filled_content, output_path)

            # 记录到历史
            history = _load_history()
            history.insert(0, {
                "template_name": template_name,
                "output_name": output_name,
                "model": model_provider or "default",
                "created_at": datetime.now().isoformat(),
                "input_preview": user_input[:100] if user_input else "",
            })
            # 最多保留50条
            history = history[:50]
            _save_history(history)

            return jsonify({
                "success": True,
                "output": str(output_path),
                "output_name": output_name,
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/history", methods=["GET"])
    def get_history():
        """获取生成历史记录"""
        try:
            history = _load_history()
            return jsonify(history)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/history/clear", methods=["POST"])
    def clear_history():
        """清除生成历史"""
        try:
            _save_history([])
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/output/<filename>")
    def download_output(filename):
        """下载生成的文件"""
        project_root = get_project_root()
        return send_from_directory(project_root / "outputs", filename, as_attachment=True)

    return app

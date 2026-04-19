# MEMORY.md - 项目长期记忆

## 项目信息
- **项目名称**：公文写作助手（official_writer）
- **项目路径**：`/Volumes/Link/工作/高德红外/公文写作/official_writer`
- **Conda 环境**：`official_writer`（Python 3.11）
- **技术栈**：Flask + PyQt6 + python-docx + LLM（MiniMax / GLM）
- **服务地址**：`http://127.0.0.1:8765`

## 关键约定
- `config.yaml` 包含 API Key 等敏感信息，不可提交到公开仓库
- 模板使用 `{{变量名}}` 占位符，存放在 `templates/` 目录
- 生成文档输出到 `outputs/` 目录
- `conda run` 后台启动 Flask 需用 `python -c` 方式，直接 `python -m src.gui.app` 可能无法后台运行
- macOS 的 `._` 文件需在模板列表 API 中过滤
- 历史记录存储在 `outputs/.history.json`

## UI 升级要点
- 首页 Dashboard 路由为 `/`，使用 `index.html`
- 生成页面使用 4 步引导流程
- Toast 提示系统（`showToast()` 函数）
- 拖拽上传已支持
- 测试模板创建脚本在 `scripts/create_test_templates.py`
- 填充模式双模式：strict（严格提取，不改原文，未识别标红）和 polish（AI润色，自动补充）
- `VariableEngine.fill_template()` 返回 `(filled_content, sources)` 元组
- 前端模式选择卡片在步骤2，步骤3有来源统计栏和标红

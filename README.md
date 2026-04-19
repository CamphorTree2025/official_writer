# 📄 公文写作助手

基于模板的 AI 公文生成工具，通过大模型（MiniMax、GLM 等）理解用户输入内容，严格按照预设 Word 模板格式生成规范的公文文件。支持 Web 图形界面和命令行两种使用方式。

## ✨ 功能特性

### 🤖 AI 智能填充

- **📌 严格提取模式** — 只从输入内容中提取原文，不修改任何文字；未识别的变量标红提示手动填写
- **✨ AI 润色模式** — 识别并润色输入内容，缺失部分由 AI 根据公文规范自动补充
- **📊 来源标注** — 每个变量清晰标注来源：原文提取 / AI 润色 / 需手动填写

### 📝 模板驱动

- 基于 `.docx` 模板，使用 `{{变量名}}` 占位符定义公文结构
- 变量按模板中出现顺序排列，编辑时与文档结构一致
- 在线上传、预览、删除 Word 模板
- 支持通知、会议纪要、请示、工作报告、函等多种公文类型

### 🖥️ Web 界面

- **4 步引导式生成**：选择模板 → 输入描述 → AI 预览编辑 → 下载文档
- **动态模型选择**：自动加载已配置的 LLM 提供商，未配置 API Key 时提示引导
- **实时预览编辑**：生成前可预览并手动修改 AI 填充的变量值，空变量自动检测
- **API 配置管理**：在线查看/修改 LLM 提供商配置，一键测试 API 连通性

### ⚙️ 灵活配置

- 支持多个 LLM 提供商（MiniMax、GLM 等），可在线切换
- 支持在配置值中使用 `${ENV_VAR}` 语法引用环境变量
- 格式校验：自动校验填充内容是否完整、格式是否规范

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                   PyQt6 Desktop Shell                        │
│              (内嵌浏览器 + 本地Web服务)                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    Flask Web Server (:8765)                   │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│   │ 首页      │  │ API配置   │  │ 模板管理  │  │ 公文生成  │   │
│   │ Dashboard│  │ 路由      │  │ 路由      │  │ 路由      │   │
│   └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                 Core Engine (复用)                            │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐   │
│  │ TemplateParser │  │ VariableEngine │  │ DocxGenerator│   │
│  │ (模板解析)      │  │ (变量填充引擎)  │  │ (文档生成)    │   │
│  └────────────────┘  └───────┬────────┘  └──────────────┘   │
│                              │                               │
│              ┌───────────────▼───────────────┐               │
│              │    LLM Adapters (可扩展)        │               │
│              │  MiniMax │ GLM │ ...           │               │
│              └───────────────────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

## 📁 目录结构

```
official_writer/
├── README.md                    # 本文件
├── SPEC.md                      # 技术规格说明
├── config.yaml                  # 配置文件（LLM提供商、模板参数）
├── requirements.txt             # Python 依赖
├── scripts/
│   └── create_test_templates.py # 测试模板创建脚本
├── templates/                   # Word 模板目录
│   ├── 通知模板.docx
│   ├── 会议纪要模板.docx
│   ├── 请示模板.docx
│   ├── 工作报告模板.docx
│   └── 函模板.docx
├── outputs/                     # 生成公文输出目录
│   └── .history.json            # 生成历史记录
├── src/
│   ├── cli.py                   # 命令行入口
│   ├── desktop.py               # PyQt6 桌面入口
│   ├── config.py                # 配置管理（YAML加载、环境变量解析）
│   ├── core/
│   │   ├── template_parser.py   # 模板解析（提取变量，保持出现顺序）
│   │   ├── variable_engine.py   # 变量替换引擎（严格/润色双模式）
│   │   └── format_validator.py  # 格式校验
│   ├── llm/
│   │   ├── base.py              # LLM 抽象基类
│   │   ├── minimax.py           # MiniMax 适配器
│   │   ├── glm.py               # 智谱 GLM 适配器
│   │   └── factory.py           # LLM 工厂类
│   ├── gui/
│   │   ├── app.py               # Flask 应用（路由定义）
│   │   ├── static/
│   │   │   ├── css/style.css    # 样式
│   │   │   └── js/main.js       # 公共JS
│   │   └── templates/           # Jinja2 页面模板
│   │       ├── base.html        # 基础布局
│   │       ├── index.html       # 首页 Dashboard
│   │       ├── generate.html    # 公文生成页（4步引导）
│   │       ├── templates.html   # 模板管理页
│   │       └── config.html      # API 配置页
│   └── output/
│       └── docx_generator.py    # Word 文档生成
└── tests/
    └── test_pipeline.py         # 端到端测试
```

## 🚀 快速开始

### 环境要求

- **Python** 3.11+
- **Conda**（推荐）或 venv 管理虚拟环境
- **操作系统**：macOS / Windows / Linux

### 1. 创建虚拟环境

```bash
# 使用 Conda（推荐）
conda create -n official_writer python=3.11
conda activate official_writer

# 或使用 venv
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

> 如不需要桌面窗口（PyQt6），可仅安装核心依赖：
> ```bash
> pip install python-docx pyyaml httpx click pydantic Flask
> ```

### 3. 配置 LLM 提供商

编辑 `config.yaml`，填入 API Key：

```yaml
llm:
  default_provider: minimax
  providers:
    minimax:
      api_key: "your-minimax-api-key"
      base_url: "https://api.minimaxi.com/v1"
      group_id: "your-group-id"
      model: "MiniMax-M2.7"
    glm:
      api_key: "your-glm-api-key"
      model: "glm-4"
      base_url: "https://open.bigmodel.cn/api/paas/v4"
```

> 💡 也可通过 Web 界面的「API 配置」页面在线设置，无需手动编辑文件。

### 4. 启动应用

#### 方式一：Web 服务（推荐）

```bash
# Conda 环境
conda run -n official_writer python -c "from src.gui.app import create_app; app = create_app(); app.run(host='127.0.0.1', port=8765)"

# 或激活环境后直接运行
conda activate official_writer
python -m src.gui.app
```

#### 方式二：桌面窗口

```bash
conda activate official_writer
python -m src.desktop
```

启动后自动打开浏览器访问 `http://127.0.0.1:8765`。

#### 方式三：命令行

```bash
# 查看模板信息
python -m src.cli info templates/通知模板.docx

# 生成公文
python -m src.cli generate \
    --template templates/通知模板.docx \
    --input "关于召开安全生产工作会议的通知" \
    --output outputs/公文.docx \
    --model minimax
```

#### 后台启动

```bash
cd /Volumes/Link/工作/高德红外/公文写作/official_writer
nohup conda run -n official_writer python -c \
  "from src.gui.app import create_app; app = create_app(); app.run(host='127.0.0.1', port=8765, debug=False)" \
  > server.log 2>&1 &
```

#### 停止服务

```bash
pkill -f "src.gui.app"
```

## 🌐 Web 界面

启动后访问 http://127.0.0.1:8765

| 页面 | 路径 | 功能说明 |
|------|------|----------|
| 🏠 首页 | `/` | Dashboard 概览，快捷入口 |
| 📝 生成公文 | `/generate` | 4 步引导：选择模板 → 输入描述 → AI 预览编辑 → 下载文档 |
| 📋 模板管理 | `/templates` | 上传、预览、删除 Word 模板文件 |
| ⚙️ API 配置 | `/config` | 查看/修改 LLM 提供商配置、测试 API 连通性 |

### 生成公文流程

1. **选择模板** — 从已有模板列表中选择，或上传新模板
2. **输入描述** — 填写公文内容描述，选择 AI 模型和填充模式
   - 📌 **严格提取**：只从输入中提取原文，不改任何文字，未识别变量标红
   - ✨ **AI 润色**：识别+润色输入内容，缺失部分由 AI 自动补充
3. **预览编辑** — 查看 AI 填充结果，手动修改不满意的变量值
4. **下载文档** — 确认无误后生成 `.docx` 文件并下载

## 📋 模板制作

在 Word 文档中使用 `{{变量名}}` 标记占位符，例如：

```
关于召开{{会议名称}}的通知

{{发文机关}} {{发文字号}}

{{日期}}

各位同事：

    {{正文内容}}

                    {{落款单位}}
                    {{日期}}
```

系统会自动识别模板中的所有变量，调用 AI 根据用户描述生成对应内容，并保持模板原有格式输出。

> 💡 变量在预览编辑页面的显示顺序与模板中出现顺序一致。

## 🔌 API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/config` | 获取当前 LLM 配置 |
| POST | `/api/config` | 保存 LLM 配置 |
| DELETE | `/api/config/provider/<name>` | 删除指定提供商配置 |
| POST | `/api/config/test` | 测试 API 连通性 |
| GET | `/api/templates` | 列出所有模板 |
| GET | `/api/template/preview?name=xxx` | 预览模板内容 |
| GET | `/api/template/variables?name=xxx` | 获取模板变量列表（按出现顺序） |
| POST | `/api/template/upload` | 上传模板文件 |
| POST | `/api/template/delete` | 删除模板文件 |
| POST | `/api/preview` | AI 预览变量填充（支持 strict/polish 模式） |
| POST | `/api/generate` | 生成公文文档 |
| GET | `/api/output/<filename>` | 下载生成的文档 |

### `/api/preview` 请求示例

```json
{
  "template_name": "通知模板.docx",
  "input": "关于召开安全生产会议的通知，时间是12月15日",
  "model": "minimax",
  "mode": "strict"
}
```

响应：

```json
{
  "variables": {
    "会议名称": "安全生产会议",
    "发文机关": "",
    "发文字号": "",
    "正文内容": "",
    "落款单位": "",
    "日期": "12月15日"
  },
  "sources": {
    "会议名称": "extracted",
    "发文机关": "manual",
    "发文字号": "manual",
    "正文内容": "manual",
    "落款单位": "manual",
    "日期": "extracted"
  },
  "mode": "strict"
}
```

## 📦 依赖项

| 依赖 | 版本 | 用途 | 必需 |
|------|------|------|------|
| python-docx | >= 1.1.0 | Word 文档读写 | ✅ |
| pyyaml | >= 6.0 | YAML 配置解析 | ✅ |
| httpx | >= 0.27.0 | HTTP 客户端（调用 LLM API） | ✅ |
| click | >= 8.1.0 | 命令行框架 | ✅ |
| pydantic | >= 2.0.0 | 数据校验 | ✅ |
| Flask | >= 3.0.0 | Web 服务 | ✅ |
| PyQt6 | >= 6.6.0 | 桌面窗口 | 可选 |
| PyQt6-WebEngine | >= 6.6.0 | 内嵌浏览器 | 可选 |

## ⚠️ 注意事项

- `config.yaml` 中包含 API Key 等敏感信息，请勿提交到公开仓库
- 支持在配置值中使用 `${ENV_VAR}` 语法引用环境变量
- 如不需要桌面窗口，可仅安装 Flask 依赖，通过浏览器访问 Web 界面
- 生成的公文默认保存在 `outputs/` 目录
- 变量解析按模板中出现顺序排列，确保预览编辑与文档结构一致

## 📄 许可证


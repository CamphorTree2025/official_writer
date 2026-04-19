# 公文写作助手

基于模板的 AI 公文生成工具，通过大模型（MiniMax、GLM 等）理解用户输入内容，严格按照预设 Word 模板格式生成规范的公文文件。支持命令行和 Web 图形界面两种使用方式。

## 功能特性

- 📝 **模板驱动** — 基于 `.docx` 模板，使用 `{{变量名}}` 占位符定义公文结构
- 🤖 **AI 填充** — 调用大模型自动理解用户意图，生成规范的公文内容
- 🖥️ **双模式运行** — 支持命令行（CLI）和 Web 图形界面
- ⚙️ **灵活配置** — 支持多个 LLM 提供商，可在线切换和测试 API 连接
- 📋 **模板管理** — 在线上传、预览、删除 Word 模板
- ✏️ **预览编辑** — 生成前可预览并手动修改 AI 填充的变量值
- ✅ **格式校验** — 自动校验填充内容是否完整、格式是否规范

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                   PyQt6 Desktop Shell                        │
│              (内嵌浏览器 + 本地Web服务)                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    Flask Web Server                           │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│   │ API配置   │  │ 模板管理  │  │ 公文生成  │                  │
│   │ 路由      │  │ 路由      │  │ 路由      │                  │
│   └──────────┘  └──────────┘  └──────────┘                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                 Core Engine (复用)                            │
│  (template_parser, variable_engine, llm adapters, docx_gen)  │
└─────────────────────────────────────────────────────────────┘
```

## 目录结构

```
official_writer/
├── README.md               # 本文件
├── SPEC.md                 # 技术规格说明
├── config.yaml             # 配置文件（LLM提供商、模板参数）
├── requirements.txt        # Python 依赖
├── templates/              # Word 模板目录
│   └── 会议纪要模版.docx
├── outputs/                # 生成公文输出目录
├── src/
│   ├── cli.py              # 命令行入口
│   ├── desktop.py          # PyQt6 桌面入口
│   ├── config.py           # 配置管理（YAML加载、环境变量解析）
│   ├── core/
│   │   ├── template_parser.py   # 模板解析（提取变量）
│   │   ├── variable_engine.py   # 变量替换引擎（调用LLM填充）
│   │   └── format_validator.py  # 格式校验
│   ├── llm/
│   │   ├── base.py         # LLM 抽象基类
│   │   ├── minimax.py      # MiniMax 适配器
│   │   ├── glm.py          # 智谱 GLM 适配器
│   │   └── factory.py      # LLM 工厂类
│   ├── gui/
│   │   ├── app.py          # Flask 应用（路由定义）
│   │   ├── routes/         # 路由模块
│   │   └── static/         # CSS/JS 静态资源
│   └── output/
│       └── docx_generator.py    # Word 文档生成
└── tests/
    └── test_pipeline.py    # 端到端测试
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 LLM 提供商

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

> 也可通过 Web 界面的「API 配置」页面在线设置，无需手动编辑文件。

### 3. 启动应用

#### 图形界面（推荐）

```bash
python -m src.desktop
```

启动后自动打开浏览器访问 `http://localhost:8765`。

#### 命令行

```bash
# 查看模板信息
python -m src.cli info templates/会议纪要模版.docx

# 生成公文
python -m src.cli generate \
    --template templates/会议纪要模版.docx \
    --input "关于召开安全生产工作会议的通知" \
    --output outputs/公文.docx \
    --model minimax
```

#### 仅启动 Web 服务（不需要 PyQt6）

```bash
python -m src.gui.app
```

然后手动打开浏览器访问 `http://localhost:8765`。

## Web 界面说明

| 页面 | 路径 | 功能 |
|------|------|------|
| API 配置 | `/config` | 查看/修改 LLM 提供商配置、测试 API 连通性 |
| 模板管理 | `/templates` | 上传、预览、删除 Word 模板文件 |
| 公文生成 | `/generate` | 选择模板 → 输入描述 → AI 预览填充 → 确认生成 → 下载文档 |

## 模板制作

在 Word 文档中使用 `{{变量名}}` 标记占位符，例如：

```
关于召开{{会议名称}}的通知

{{日期}}

各位同事：

{{正文内容}}

{{落款}}
```

系统会自动识别模板中的所有变量，调用 AI 根据用户描述生成对应内容，并保持模板原有格式输出。

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/config` | 获取当前 LLM 配置 |
| POST | `/api/config` | 保存 LLM 配置 |
| DELETE | `/api/config/provider/<name>` | 删除指定提供商配置 |
| POST | `/api/config/test` | 测试 API 连通性 |
| GET | `/api/templates` | 列出所有模板 |
| GET | `/api/template/preview?name=xxx` | 预览模板内容 |
| GET | `/api/template/variables?name=xxx` | 获取模板变量列表 |
| POST | `/api/template/upload` | 上传模板文件 |
| POST | `/api/template/delete` | 删除模板文件 |
| POST | `/api/preview` | AI 预览变量填充结果 |
| POST | `/api/generate` | 生成公文文档 |
| GET | `/api/output/<filename>` | 下载生成的文档 |

## 依赖项

| 依赖 | 版本 | 用途 |
|------|------|------|
| python-docx | >= 1.1.0 | Word 文档读写 |
| pyyaml | >= 6.0 | YAML 配置解析 |
| httpx | >= 0.27.0 | HTTP 客户端（调用 LLM API） |
| click | >= 8.1.0 | 命令行框架 |
| pydantic | >= 2.0.0 | 数据校验 |
| Flask | >= 3.0.0 | Web 服务 |
| PyQt6 | >= 6.6.0 | 桌面窗口（可选） |
| PyQt6-WebEngine | >= 6.6.0 | 内嵌浏览器（可选） |

## 注意事项

- `config.yaml` 中包含 API Key 等敏感信息，请勿提交到公开仓库
- 支持在配置值中使用 `${ENV_VAR}` 语法引用环境变量
- 如不需要桌面窗口，可仅安装 Flask 依赖，通过浏览器访问 Web 界面
- 生成的公文默认保存在 `outputs/` 目录

## 许可证

内部使用 — 高德红外

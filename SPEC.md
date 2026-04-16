# 公文写作助手 - 技术规格说明

## 项目概述

基于模板的AI公文生成工具，通过大模型（Minimax、GLM等）理解用户输入内容，严格按照预设Word模板格式生成规范的公文文件。支持命令行和Web图形界面两种使用方式。

## 技术架构

### 整体架构

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

### 目录结构

```
公文写作/
├── SPEC.md
├── requirements.txt       # Python依赖
├── config.yaml            # 配置文件
├── templates/             # 模板目录(.docx)
├── src/
│   ├── cli.py             # 命令行入口
│   ├── desktop.py         # PyQt6桌面入口
│   ├── config.py          # 配置管理
│   ├── core/
│   │   ├── template_parser.py    # 模板解析
│   │   ├── variable_engine.py    # 变量替换
│   │   └── format_validator.py   # 格式校验
│   ├── llm/
│   │   ├── base.py        # LLM基类
│   │   ├── minimax.py     # Minimax适配器
│   │   ├── glm.py         # GLM适配器
│   │   └── factory.py     # 工厂类
│   ├── gui/
│   │   ├── app.py         # Flask应用
│   │   ├── routes/        # 路由模块
│   │   └── static/        # CSS/JS资源
│   └── output/
│       └── docx_generator.py     # Word生成
├── templates/             # HTML页面模板
└── outputs/              # 输出目录
```

## 功能模块

### 1. 配置管理 (config.py)

- 加载YAML配置文件
- 支持环境变量引用 `${VAR_NAME}`
- 提供默认提供商配置

### 2. 模板解析 (template_parser.py)

- 解析`.docx`文件
- 识别`{{变量名}}`占位符
- 提取段落和表格中的变量

### 3. LLM适配层

- `LLMBase`: 抽象基类
- `MinimaxAdapter`: Minimax模型适配
- `GLMAdapter`: 智谱GLM模型适配
- `LLMFactory`: 工厂类，按配置返回适配器

### 4. 变量替换引擎 (variable_engine.py)

- 构造提示词调用LLM
- 解析返回内容填充变量
- 支持上下文信息

### 5. Word生成 (docx_generator.py)

- 基于python-docx
- 保持原模板格式
- 替换`{{}}`为填充内容

### 6. Web图形界面 (gui/)

- **Flask应用**: 提供RESTful API
- **API配置页面**: 配置各LLM提供商的API Key
- **模板管理页面**: 查看和管理模板文件
- **公文生成页面**: 选择模板、输入内容、生成公文

## 使用方式

### 图形界面（推荐）

```bash
# 安装依赖
pip install -r requirements.txt

# 启动图形界面
python -m src.desktop

# 浏览器自动打开 http://localhost:8765
```

### 命令行

```bash
# 查看模板信息
python -m src.cli info templates/模板.docx

# 生成公文
python -m src.cli generate \
    --template templates/模板.docx \
    --input "关于召开安全生产工作会议的通知" \
    --output outputs/公文.docx \
    --model minimax
```

## Web界面功能

### API配置页面 (`/config`)

- 查看当前配置状态
- 设置默认LLM提供商
- 配置各提供商的API Key和模型参数
- 保存配置到config.yaml

### 模板管理页面 (`/templates`)

- 列出templates目录下的所有.docx模板
- 显示模板文件大小
- 查看模板使用说明

### 公文生成页面 (`/generate`)

- 选择模板文件
- 选择LLM模型
- 输入公文内容描述
- 设置输出文件名
- 一键生成并下载

## 配置示例 (config.yaml)

```yaml
llm:
  default_provider: "minimax"
  providers:
    minimax:
      api_key: "${MINIMAX_API_KEY}"
      model: "abab6.5s"
      base_url: "https://api.minimax.chat/v1"
    glm:
      api_key: "${GLM_API_KEY}"
      model: "glm-4"
      base_url: "https://open.bigmodel.cn/api/paas/v4"

template:
  variable_pattern: "{{(.*?)}}"
  default_variables:
    date: "{{CURRENT_DATE}}"
    author: "办公室"
```

## 模板示例

在Word模板中使用`{{变量名}}`标注占位符：

```
关于召开{{会议名称}}的通知

{{日期}}

各位同事：

{{正文内容}}

{{落款}}
```

## 依赖项

### 核心依赖

- python-docx >= 1.1.0
- pyyaml >= 6.0
- httpx >= 0.27.0
- click >= 8.1.0
- pydantic >= 2.0.0

### Web界面依赖

- Flask >= 3.0.0
- PyQt6 >= 6.6.0
- PyQt6-WebEngine >= 6.6.0

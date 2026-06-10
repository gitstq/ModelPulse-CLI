<p align="center">
  <img src="logo.jpg" alt="ModelPulse-CLI Logo" width="200" height="200">
</p>

<h1 align="center">ModelPulse-CLI</h1>

<p align="center">
  <strong>轻量级终端AI模型实时监控与智能推荐引擎</strong>
</p>

<p align="center">
  <a href="https://github.com/gitstq/ModelPulse-CLI/releases"><img src="https://img.shields.io/badge/版本-1.0.0-blue.svg" alt="版本"></a>
  <a href="https://github.com/gitstq/ModelPulse-CLI/blob/main/LICENSE"><img src="https://img.shields.io/badge/协议-MIT-green.svg" alt="协议"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python"></a>
  <img src="https://img.shields.io/badge/依赖-零依赖-green.svg" alt="零依赖">
  <img src="https://img.shields.io/badge/平台-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg" alt="跨平台">
  <img src="https://img.shields.io/badge/模型数-21-orange.svg" alt="21个模型">
  <img src="https://img.shields.io/badge/提供商-7-purple.svg" alt="7个提供商">
</p>

<p align="center">
  简体中文 | <a href="README.zh-TW.md">繁體中文</a> | <a href="README.md">English</a>
</p>

---

## 项目介绍

ModelPulse-CLI 是一款零依赖、跨平台的终端工具，帮助开发者**监控AI模型API状态**、**对比模型性能**、**估算成本**，并根据具体使用场景**获取智能推荐**。

覆盖 **7大主流提供商的21个模型**（OpenAI、Anthropic、Google、DeepSeek、Meta、Qwen、Mistral），包含基准测试分数、定价数据和智能评分算法。

## 核心特性

- **模型注册表** - 浏览21个AI模型的详细规格、基准分数和定价
- **智能推荐** - 基于7种任务类型获取个性化模型建议（编码、推理、视觉等）
- **API监控** - 实时端点健康检查与延迟测量
- **并排对比** - 跨所有指标对比任意模型
- **定价仪表盘** - 成本分析，自动识别最便宜/最贵的模型
- **多格式导出** - 支持导出为JSON、CSV或Markdown格式
- **历史追踪** - 90天的监控和推荐历史记录
- **零依赖** - 纯Python标准库，无需pip安装
- **跨平台** - 支持Linux、macOS和Windows

## 快速开始

### 方式一：直接运行（无需安装）

```bash
# 克隆仓库
git clone https://github.com/gitstq/ModelPulse-CLI.git
cd ModelPulse-CLI

# 直接运行
PYTHONPATH=src python3 -m modelpulse.cli list
```

### 方式二：通过pip安装

```bash
git clone https://github.com/gitstq/ModelPulse-CLI.git
cd ModelPulse-CLI
pip install -e .

# 直接使用命令
modelpulse list
```

### 常用命令

```bash
# 列出所有模型
modelpulse list

# 按价格排序
modelpulse list --sort price

# 按提供商筛选
modelpulse list --provider openai

# 监控API端点状态
modelpulse monitor

# 获取代码生成任务的模型推荐
modelpulse recommend --task code_generation

# 并排对比模型
modelpulse compare "gpt-4o,claude-sonnet-4-20250514,gemini-2.5-pro"

# 查看定价仪表盘
modelpulse pricing

# 导出为CSV
modelpulse export --format csv -o models.csv

# 查看可用任务类型
modelpulse tasks
```

## 详细使用指南

### `modelpulse list` - 模型注册表

列出所有追踪的AI模型及其详细信息。

| 参数 | 说明 |
|------|------|
| `--provider, -p` | 按提供商筛选（如 openai、anthropic） |
| `--category, -c` | 按类别筛选（flagship、cost_effective、reasoning、open_source、specialized） |
| `--sort, -s` | 排序方式：name、price、context、mmlu、math |

### `modelpulse recommend` - 智能推荐

根据任务类型获取AI模型推荐。

| 参数 | 说明 |
|------|------|
| `--task, -t` | 任务类型（必填）：general_chat、code_generation、reasoning、vision、long_context、cost_sensitive、function_calling |
| `--top, -n` | 推荐数量（默认：5） |
| `--api-key` | 仅从已配置API密钥的提供商中推荐 |

**可用任务类型：**
- `general_chat` - 通用对话与问答
- `code_generation` - 代码编写与软件工程
- `reasoning` - 复杂数学与逻辑推理
- `vision` - 图像理解与视觉分析
- `long_context` - 长文档与长对话处理
- `cost_sensitive` - 高并发、成本优化场景
- `function_calling` - 智能体工作流与工具调用

### `modelpulse monitor` - API端点监控

实时检查提供商API端点的可用性和延迟。

| 参数 | 说明 |
|------|------|
| `--timeout, -t` | 请求超时时间（秒，默认：10） |

### `modelpulse compare` - 模型对比

跨所有指标并排对比模型。

```bash
modelpulse compare "gpt-4o,claude-sonnet-4-20250514,gemini-2.5-pro"
```

### `modelpulse pricing` - 定价仪表盘

查看和对比所有模型的定价。

| 参数 | 说明 |
|------|------|
| `--provider, -p` | 按提供商筛选 |

### `modelpulse export` - 数据导出

将模型数据库导出为多种格式。

| 参数 | 说明 |
|------|------|
| `--format, -f` | 输出格式：json、csv、markdown |
| `--output, -o` | 输出文件路径 |

### `modelpulse config` - 配置管理

管理API密钥和偏好设置。

```bash
# 查看当前配置
modelpulse config --show

# 设置提供商API密钥
modelpulse config --set-key openai=sk-your-key-here
```

### `modelpulse history` - 历史数据

查看过去的监控和推荐记录。

| 参数 | 说明 |
|------|------|
| `--type, -t` | 按类型筛选：monitor、recommend |
| `--limit, -n` | 显示记录数量 |

## 设计思路

1. **零依赖** - 完全基于Python标准库构建，无需pip安装即可运行
2. **离线优先** - 所有模型数据内嵌，无网络也可进行列表/对比/推荐
3. **可扩展** - 通过编辑单一数据结构即可添加新模型、提供商和任务配置
4. **开发者友好** - 清晰的输出格式、颜色支持和结构化数据导出
5. **跨平台** - 在Linux、macOS和Windows上测试通过，无平台特定依赖

## 迭代规划

- [ ] Web仪表盘模式（HTML报告生成）
- [ ] 从提供商API自动更新模型数据库
- [ ] Token用量追踪与预算告警
- [ ] 插件系统（自定义评分算法）
- [ ] 交互式TUI模式（键盘导航）
- [ ] 模型微调成本计算器
- [ ] 多语言模型名称支持（中/日/韩）
- [ ] CI/CD集成（GitHub Actions徽章）

## 技术栈

| 组件 | 技术 |
|------|------|
| 语言 | Python 3.10+ |
| 依赖 | 无（仅标准库） |
| 终端UI | ANSI转义码 |
| 数据存储 | JSON（本地文件系统） |
| 测试框架 | unittest（标准库） |
| 包管理器 | pip / setuptools |

## 项目结构

```
ModelPulse-CLI/
├── src/modelpulse/
│   ├── __init__.py      # 包元数据
│   ├── cli.py           # 主CLI入口与模型数据库
│   ├── engine.py        # 评分、成本分析、趋势追踪
│   ├── models.py        # 数据模型定义
│   └── tui.py           # 终端UI组件
├── tests/
│   └── test_modelpulse.py  # 24个单元测试
├── data/                # 用户数据目录（已gitignore）
├── pyproject.toml       # 包配置
├── .gitignore
├── LICENSE              # MIT协议
├── CONTRIBUTING.md      # 贡献指南
├── logo.jpg             # 项目Logo
└── README.zh-CN.md      # 本文件
```

## 贡献指南

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

快速步骤：
1. Fork 本仓库
2. 创建功能分支
3. 添加/更新测试
4. 提交 Pull Request

## 开源协议

本项目基于 MIT 协议开源 - 详见 [LICENSE](LICENSE) 文件。

---

<p align="center">
  由 <a href="https://github.com/gitstq">ModelPulse Team</a> 用 ❤️ 构建
</p>

<p align="center">
  <img src="logo.jpg" alt="ModelPulse-CLI Logo" width="200" height="200">
</p>

<h1 align="center">ModelPulse-CLI</h1>

<p align="center">
  <strong>輕量級終端AI模型即時監控與智慧推薦引擎</strong>
</p>

<p align="center">
  <a href="https://github.com/gitstq/ModelPulse-CLI/releases"><img src="https://img.shields.io/badge/版本-1.0.0-blue.svg" alt="版本"></a>
  <a href="https://github.com/gitstq/ModelPulse-CLI/blob/main/LICENSE"><img src="https://img.shields.io/badge/協議-MIT-green.svg" alt="協議"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python"></a>
  <img src="https://img.shields.io/badge/依賴-零依賴-green.svg" alt="零依賴">
  <img src="https://img.shields.io/badge/平台-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg" alt="跨平台">
  <img src="https://img.shields.io/badge/模型數-21-orange.svg" alt="21個模型">
  <img src="https://img.shields.io/badge/提供商-7-purple.svg" alt="7個提供商">
</p>

<p align="center">
  <a href="README.zh-CN.md">简体中文</a> | 繁體中文 | <a href="README.md">English</a>
</p>

---

## 專案介紹

ModelPulse-CLI 是一款零依賴、跨平台的終端工具，協助開發者**監控AI模型API狀態**、**對比模型效能**、**估算成本**，並根據具體使用場景**取得智慧推薦**。

涵蓋 **7大主流提供商的21個模型**（OpenAI、Anthropic、Google、DeepSeek、Meta、Qwen、Mistral），包含基準測試分數、定價資料與智慧評分演算法。

## 核心特性

- **模型註冊表** - 瀏覽21個AI模型的詳細規格、基準分數與定價
- **智慧推薦** - 基於7種任務類型取得個人化模型建議（編碼、推理、視覺等）
- **API監控** - 即時端點健康檢查與延遲測量
- **並排對比** - 跨所有指標對比任意模型
- **定僱儀表盤** - 成本分析，自動識別最便宜/最貴的模型
- **多格式匯出** - 支援匯出為JSON、CSV或Markdown格式
- **歷史追蹤** - 90天的監控與推薦歷史記錄
- **零依賴** - 純Python標準庫，無需pip安裝
- **跨平台** - 支援Linux、macOS和Windows

## 快速開始

### 方式一：直接執行（無需安裝）

```bash
# 克隆倉庫
git clone https://github.com/gitstq/ModelPulse-CLI.git
cd ModelPulse-CLI

# 直接執行
PYTHONPATH=src python3 -m modelpulse.cli list
```

### 方式二：透過pip安裝

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

# 按價格排序
modelpulse list --sort price

# 按提供商篩選
modelpulse list --provider openai

# 監控API端點狀態
modelpulse monitor

# 取得程式碼生成任務的模型推薦
modelpulse recommend --task code_generation

# 並排對比模型
modelpulse compare "gpt-4o,claude-sonnet-4-20250514,gemini-2.5-pro"

# 查看定僱儀表盤
modelpulse pricing

# 匯出為CSV
modelpulse export --format csv -o models.csv

# 查看可用任務類型
modelpulse tasks
```

## 詳細使用指南

### `modelpulse list` - 模型註冊表

列出所有追蹤的AI模型及其詳細資訊。

| 參數 | 說明 |
|------|------|
| `--provider, -p` | 按提供商篩選（如 openai、anthropic） |
| `--category, -c` | 按類別篩選（flagship、cost_effective、reasoning、open_source、specialized） |
| `--sort, -s` | 排序方式：name、price、context、mmlu、math |

### `modelpulse recommend` - 智慧推薦

根據任務類型取得AI模型推薦。

| 參數 | 說明 |
|------|------|
| `--task, -t` | 任務類型（必填）：general_chat、code_generation、reasoning、vision、long_context、cost_sensitive、function_calling |
| `--top, -n` | 推薦數量（預設：5） |
| `--api-key` | 僅從已設定API金鑰的提供商中推薦 |

**可用任務類型：**
- `general_chat` - 通用對話與問答
- `code_generation` - 程式碼編寫與軟體工程
- `reasoning` - 複雜數學與邏輯推理
- `vision` - 影像理解與視覺分析
- `long_context` - 長文件與長對話處理
- `cost_sensitive` - 高並發、成本最佳化場景
- `function_calling` - 智慧體工作流與工具呼叫

### `modelpulse monitor` - API端點監控

即時檢查提供商API端點的可用性與延遲。

| 參數 | 說明 |
|------|------|
| `--timeout, -t` | 請求逾時時間（秒，預設：10） |

### `modelpulse compare` - 模型對比

跨所有指標並排對比模型。

```bash
modelpulse compare "gpt-4o,claude-sonnet-4-20250514,gemini-2.5-pro"
```

### `modelpulse pricing` - 定僱儀表盤

查看與對比所有模型的定僱。

| 參數 | 說明 |
|------|------|
| `--provider, -p` | 按提供商篩選 |

### `modelpulse export` - 資料匯出

將模型資料庫匯出為多種格式。

| 參數 | 說明 |
|------|------|
| `--format, -f` | 輸出格式：json、csv、markdown |
| `--output, -o` | 輸出檔案路徑 |

### `modelpulse config` - 設定管理

管理API金鑰與偏好設定。

```bash
# 查看當前設定
modelpulse config --show

# 設定提供商API金鑰
modelpulse config --set-key openai=sk-your-key-here
```

### `modelpulse history` - 歷史資料

查看過去的監控與推薦記錄。

| 參數 | 說明 |
|------|------|
| `--type, -t` | 按類型篩選：monitor、recommend |
| `--limit, -n` | 顯示記錄數量 |

## 設計思路

1. **零依賴** - 完全基於Python標準庫建構，無需pip安裝即可執行
2. **離線優先** - 所有模型資料內嵌，無網路也可進行列表/對比/推薦
3. **可擴展** - 透過編輯單一資料結構即可新增模型、提供商與任務設定
4. **開發者友善** - 清晰的輸出格式、色彩支援與結構化資料匯出
5. **跨平台** - 在Linux、macOS和Windows上測試通過，無平台特定依賴

## 迭代規劃

- [ ] Web儀表盤模式（HTML報告生成）
- [ ] 從提供商API自動更新模型資料庫
- [ ] Token用量追蹤與預算告警
- [ ] 外掛系統（自訂評分演算法）
- [ ] 互動式TUI模式（鍵盤導航）
- [ ] 模型微調成本計算器
- [ ] 多語言模型名稱支援（中/日/韓）
- [ ] CI/CD整合（GitHub Actions徽章）

## 技術棧

| 組件 | 技術 |
|------|------|
| 語言 | Python 3.10+ |
| 依賴 | 無（僅標準庫） |
| 終端UI | ANSI跳脫碼 |
| 資料儲存 | JSON（本地檔案系統） |
| 測試框架 | unittest（標準庫） |
| 套件管理器 | pip / setuptools |

## 專案結構

```
ModelPulse-CLI/
├── src/modelpulse/
│   ├── __init__.py      # 套件元資料
│   ├── cli.py           # 主CLI入口與模型資料庫
│   ├── engine.py        # 評分、成本分析、趨勢追蹤
│   ├── models.py        # 資料模型定義
│   └── tui.py           # 終端UI組件
├── tests/
│   └── test_modelpulse.py  # 24個單元測試
├── data/                # 使用者資料目錄（已gitignore）
├── pyproject.toml       # 套件設定
├── .gitignore
├── LICENSE              # MIT協議
├── CONTRIBUTING.md      # 貢獻指南
├── logo.jpg             # 專案Logo
└── README.zh-TW.md      # 本檔案
```

## 貢獻指南

歡迎貢獻！請查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解詳情。

快速步驟：
1. Fork 本倉庫
2. 建立功能分支
3. 新增/更新測試
4. 提交 Pull Request

## 開源協議

本專案基於 MIT 協議開源 - 詳見 [LICENSE](LICENSE) 檔案。

---

<p align="center">
  由 <a href="https://github.com/gitstq">ModelPulse Team</a> 用 ❤️ 建構
</p>

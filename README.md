<p align="center">
  <img src="logo.jpg" alt="ModelPulse-CLI Logo" width="200" height="200">
</p>

<h1 align="center">ModelPulse-CLI</h1>

<p align="center">
  <strong>Lightweight Terminal AI Model Real-time Monitoring & Intelligent Recommendation Engine</strong>
</p>

<p align="center">
  <a href="https://github.com/gitstq/ModelPulse-CLI/releases"><img src="https://img.shields.io/badge/version-1.0.0-blue.svg" alt="Version"></a>
  <a href="https://github.com/gitstq/ModelPulse-CLI/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python"></a>
  <img src="https://img.shields.io/badge/dependencies-zero-green.svg" alt="Zero Dependencies">
  <img src="https://img.shields.io/badge/platforms-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg" alt="Cross-Platform">
  <img src="https://img.shields.io/badge/models-21-orange.svg" alt="21 Models">
  <img src="https://img.shields.io/badge/providers-7-purple.svg" alt="7 Providers">
</p>

<p align="center">
  <a href="README.zh-CN.md">简体中文</a> | <a href="README.zh-TW.md">繁體中文</a> | English
</p>

---

## Introduction

ModelPulse-CLI is a zero-dependency, cross-platform terminal tool that helps developers **monitor AI model API status**, **compare model performance**, **estimate costs**, and **get smart recommendations** based on their specific use case.

Track **21 models across 7 major providers** (OpenAI, Anthropic, Google, DeepSeek, Meta, Qwen, Mistral) with benchmark scores, pricing data, and intelligent scoring algorithms.

## Core Features

- **Model Registry** - Browse 21 AI models with detailed specs, benchmarks, and pricing
- **Smart Recommendation** - Get personalized model suggestions for 7 task types (coding, reasoning, vision, etc.)
- **API Monitoring** - Real-time endpoint health checks with latency measurement
- **Side-by-Side Comparison** - Compare any models across all metrics
- **Pricing Dashboard** - Cost analysis with cheapest/most expensive detection
- **Multi-Format Export** - Export to JSON, CSV, or Markdown
- **Historical Tracking** - 90-day history of monitoring and recommendation data
- **Zero Dependencies** - Pure Python stdlib, no pip install needed
- **Cross-Platform** - Works on Linux, macOS, and Windows

## Quick Start

### Option 1: Run Directly (No Install)

```bash
# Clone the repository
git clone https://github.com/gitstq/ModelPulse-CLI.git
cd ModelPulse-CLI

# Run directly
PYTHONPATH=src python3 -m modelpulse.cli list
```

### Option 2: Install via pip

```bash
git clone https://github.com/gitstq/ModelPulse-CLI.git
cd ModelPulse-CLI
pip install -e .

# Now use the command directly
modelpulse list
```

### First Commands

```bash
# List all tracked models
modelpulse list

# List models sorted by price
modelpulse list --sort price

# Filter by provider
modelpulse list --provider openai

# Monitor API endpoint status
modelpulse monitor

# Get model recommendation for code generation
modelpulse recommend --task code_generation

# Compare models side by side
modelpulse compare "gpt-4o,claude-sonnet-4-20250514,gemini-2.5-pro"

# View pricing dashboard
modelpulse pricing

# Export to CSV
modelpulse export --format csv -o models.csv

# View available task types
modelpulse tasks
```

## Detailed Usage Guide

### `modelpulse list` - Model Registry

List all tracked AI models with detailed information.

| Flag | Description |
|------|-------------|
| `--provider, -p` | Filter by provider name (e.g., openai, anthropic) |
| `--category, -c` | Filter by category (flagship, cost_effective, reasoning, open_source, specialized) |
| `--sort, -s` | Sort by: name, price, context, mmlu, math |

### `modelpulse recommend` - Smart Recommendation

Get AI model recommendations based on task type.

| Flag | Description |
|------|-------------|
| `--task, -t` | Task type (required): general_chat, code_generation, reasoning, vision, long_context, cost_sensitive, function_calling |
| `--top, -n` | Number of recommendations (default: 5) |
| `--api-key` | Only recommend from providers with configured API keys |

**Available Task Types:**
- `general_chat` - General conversation and Q&A
- `code_generation` - Code writing and software engineering
- `reasoning` - Complex mathematical and logical reasoning
- `vision` - Image understanding and visual analysis
- `long_context` - Processing long documents and conversations
- `cost_sensitive` - High-volume, cost-optimized usage
- `function_calling` - Agent workflows and tool use

### `modelpulse monitor` - API Endpoint Monitoring

Check real-time availability and latency of provider API endpoints.

| Flag | Description |
|------|-------------|
| `--timeout, -t` | Request timeout in seconds (default: 10) |

### `modelpulse compare` - Model Comparison

Compare models side by side across all metrics.

```bash
modelpulse compare "gpt-4o,claude-sonnet-4-20250514,gemini-2.5-pro"
```

### `modelpulse pricing` - Pricing Dashboard

View and compare pricing across all models.

| Flag | Description |
|------|-------------|
| `--provider, -p` | Filter by provider |

### `modelpulse export` - Data Export

Export model database to various formats.

| Flag | Description |
|------|-------------|
| `--format, -f` | Output format: json, csv, markdown |
| `--output, -o` | Output file path |

### `modelpulse config` - Configuration

Manage API keys and preferences.

```bash
# Show current config
modelpulse config --show

# Set API key for a provider
modelpulse config --set-key openai=sk-your-key-here
```

### `modelpulse history` - Historical Data

View past monitoring and recommendation records.

| Flag | Description |
|------|-------------|
| `--type, -t` | Filter by type: monitor, recommend |
| `--limit, -n` | Number of records to show |

## Design Philosophy

1. **Zero Dependencies** - Built entirely on Python stdlib. No pip install required to run.
2. **Offline-First** - All model data is embedded. Works without internet for listing/comparison/recommendation.
3. **Extensible** - Easy to add new models, providers, and task profiles by editing a single data structure.
4. **Developer-Friendly** - Clean output formatting, color support, and structured data export.
5. **Cross-Platform** - Tested on Linux, macOS, and Windows with no platform-specific dependencies.

## Roadmap

- [ ] Web dashboard mode (HTML report generation)
- [ ] Auto-update model database from provider APIs
- [ ] Token usage tracking and budget alerts
- [ ] Plugin system for custom scoring algorithms
- [ ] Interactive TUI mode with keyboard navigation
- [ ] Model fine-tuning cost calculator
- [ ] Multi-language model name support (CN/JP/KR)
- [ ] CI/CD integration (GitHub Actions badge)

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| Dependencies | None (stdlib only) |
| Terminal UI | ANSI escape codes |
| Data Storage | JSON (local filesystem) |
| Testing | unittest (stdlib) |
| Package Manager | pip / setuptools |

## Project Structure

```
ModelPulse-CLI/
├── src/modelpulse/
│   ├── __init__.py      # Package metadata
│   ├── cli.py           # Main CLI entry point & model database
│   ├── engine.py        # Scoring, cost analysis, trend tracking
│   ├── models.py        # Data model definitions
│   └── tui.py           # Terminal UI components
├── tests/
│   └── test_modelpulse.py  # 24 unit tests
├── data/                # User data directory (gitignored)
├── pyproject.toml       # Package configuration
├── .gitignore
├── LICENSE              # MIT License
├── CONTRIBUTING.md      # Contribution guidelines
├── logo.jpg             # Project logo
└── README.md            # This file
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

Quick steps:
1. Fork the repository
2. Create a feature branch
3. Add/update tests
4. Submit a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Built with ❤️ by <a href="https://github.com/gitstq">ModelPulse Team</a>
</p>

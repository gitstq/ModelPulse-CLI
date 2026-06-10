# Contributing to ModelPulse-CLI

Thank you for your interest in contributing to ModelPulse-CLI! This document provides guidelines for contributing.

## Getting Started

### Prerequisites
- Python 3.10 or higher
- Git
- A terminal/emulator

### Setup
```bash
git clone https://github.com/gitstq/ModelPulse-CLI.git
cd ModelPulse-CLI
pip install -e .
```

### Running Tests
```bash
python -m unittest discover tests -v
```

## How to Contribute

### Reporting Bugs
1. Check existing issues first
2. Create a new issue with:
   - OS and Python version
   - Steps to reproduce
   - Expected vs actual behavior
   - Error output (if any)

### Suggesting Features
1. Open an issue with `[Feature]` prefix
2. Describe the use case clearly
3. Include example usage if possible

### Submitting Changes
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Write/update tests for your changes
4. Ensure all tests pass
5. Commit with conventional format: `feat: add new feature` / `fix: resolve issue`
6. Push and open a Pull Request

### Adding a New Model
Edit `src/modelpulse/cli.py` and add the model to `MODELS_DB` following the existing structure:
```python
"provider_key": {
    "provider": "Provider Name",
    "models": {
        "model-id": {
            "display_name": "Model Name",
            "category": "flagship|cost_effective|reasoning|open_source|specialized",
            "context_window": 128000,
            "input_price_per_1m": 0.00,
            "output_price_per_1m": 0.00,
            "capabilities": ["chat", "vision"],
            "release_date": "YYYY-MM-DD",
            "benchmark_scores": {"mmlu": 0.0, "human_eval": 0.0, "math": 0.0},
        }
    }
}
```

### Adding a New Task Profile
Add to `TASK_PROFILES` in `src/modelpulse/cli.py`:
```python
"task_key": {
    "name": "Task Name",
    "name_zh": "中文名称",
    "weights": {"mmlu": 0.3, "human_eval": 0.3, "cost": 0.4},
    "required_capabilities": ["chat"],
    "preferred_capabilities": ["json_mode"],
}
```

## Code Style
- Follow PEP 8
- Use type hints where practical
- Add docstrings to public functions/classes
- Keep functions focused and under 50 lines

## License
By contributing, you agree that your contributions will be licensed under the MIT License.

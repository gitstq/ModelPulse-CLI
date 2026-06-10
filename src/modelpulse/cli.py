"""
ModelPulse-CLI - Lightweight Terminal AI Model Real-time Monitoring & Intelligent Recommendation Engine
轻量级终端AI模型实时监控与智能推荐引擎

Zero external dependencies (stdlib only), Cross-Platform, Pure Python
"""

import argparse
import json
import os
import sys
import time
import csv
import hashlib
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import ssl

# ─── Constants ────────────────────────────────────────────────────────────────

APP_NAME = "ModelPulse-CLI"
VERSION = "1.0.0"
CONFIG_DIR = Path.home() / ".modelpulse"
DATA_DIR = CONFIG_DIR / "data"
CACHE_FILE = DATA_DIR / "cache.json"
HISTORY_FILE = DATA_DIR / "history.json"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_TIMEOUT = 10  # seconds
MAX_HISTORY_DAYS = 90

# ─── Built-in Model Database ─────────────────────────────────────────────────

MODELS_DB = {
    "openai": {
        "provider": "OpenAI",
        "models": {
            "gpt-4o": {
                "display_name": "GPT-4o",
                "category": "flagship",
                "context_window": 128000,
                "input_price_per_1m": 2.50,
                "output_price_per_1m": 10.00,
                "capabilities": ["chat", "vision", "function_calling", "json_mode"],
                "release_date": "2024-05-13",
                "benchmark_scores": {"mmlu": 88.7, "human_eval": 90.2, "math": 76.6},
            },
            "gpt-4o-mini": {
                "display_name": "GPT-4o Mini",
                "category": "cost_effective",
                "context_window": 128000,
                "input_price_per_1m": 0.15,
                "output_price_per_1m": 0.60,
                "capabilities": ["chat", "vision", "function_calling", "json_mode"],
                "release_date": "2024-07-18",
                "benchmark_scores": {"mmlu": 82.0, "human_eval": 87.2, "math": 70.2},
            },
            "gpt-4.1": {
                "display_name": "GPT-4.1",
                "category": "flagship",
                "context_window": 1047576,
                "input_price_per_1m": 2.00,
                "output_price_per_1m": 8.00,
                "capabilities": ["chat", "vision", "function_calling", "json_mode", "code_execution"],
                "release_date": "2025-04-14",
                "benchmark_scores": {"mmlu": 90.3, "human_eval": 92.1, "math": 80.5, "swe_bench": 55.0},
            },
            "gpt-4.1-mini": {
                "display_name": "GPT-4.1 Mini",
                "category": "cost_effective",
                "context_window": 1047576,
                "input_price_per_1m": 0.40,
                "output_price_per_1m": 1.60,
                "capabilities": ["chat", "vision", "function_calling", "json_mode"],
                "release_date": "2025-04-14",
                "benchmark_scores": {"mmlu": 86.5, "human_eval": 88.4, "math": 73.8},
            },
            "o3": {
                "display_name": "o3",
                "category": "reasoning",
                "context_window": 200000,
                "input_price_per_1m": 10.00,
                "output_price_per_1m": 40.00,
                "capabilities": ["chat", "reasoning", "function_calling", "code_execution", "json_mode"],
                "release_date": "2025-04-02",
                "benchmark_scores": {"mmlu": 91.2, "human_eval": 94.5, "math": 89.7, "swe_bench": 72.5},
            },
            "o3-mini": {
                "display_name": "o3 Mini",
                "category": "reasoning",
                "context_window": 200000,
                "input_price_per_1m": 1.10,
                "output_price_per_1m": 4.40,
                "capabilities": ["chat", "reasoning", "function_calling", "json_mode"],
                "release_date": "2025-01-31",
                "benchmark_scores": {"mmlu": 87.1, "human_eval": 90.8, "math": 82.3},
            },
            "o4-mini": {
                "display_name": "o4 Mini",
                "category": "reasoning",
                "context_window": 200000,
                "input_price_per_1m": 1.10,
                "output_price_per_1m": 4.40,
                "capabilities": ["chat", "reasoning", "function_calling", "json_mode", "code_execution"],
                "release_date": "2025-06-05",
                "benchmark_scores": {"mmlu": 89.0, "human_eval": 92.3, "math": 85.1, "swe_bench": 65.8},
            },
        },
    },
    "anthropic": {
        "provider": "Anthropic",
        "models": {
            "claude-sonnet-4-20250514": {
                "display_name": "Claude Sonnet 4",
                "category": "flagship",
                "context_window": 200000,
                "input_price_per_1m": 3.00,
                "output_price_per_1m": 15.00,
                "capabilities": ["chat", "vision", "function_calling", "json_mode", "code_execution"],
                "release_date": "2025-05-14",
                "benchmark_scores": {"mmlu": 89.5, "human_eval": 93.1, "math": 81.2, "swe_bench": 62.0},
            },
            "claude-haiku-3-5-20241022": {
                "display_name": "Claude 3.5 Haiku",
                "category": "cost_effective",
                "context_window": 200000,
                "input_price_per_1m": 0.80,
                "output_price_per_1m": 4.00,
                "capabilities": ["chat", "vision", "function_calling", "json_mode"],
                "release_date": "2024-11-04",
                "benchmark_scores": {"mmlu": 84.3, "human_eval": 88.9, "math": 72.5},
            },
            "claude-opus-4-20250514": {
                "display_name": "Claude Opus 4",
                "category": "flagship",
                "context_window": 200000,
                "input_price_per_1m": 15.00,
                "output_price_per_1m": 75.00,
                "capabilities": ["chat", "vision", "function_calling", "json_mode", "code_execution"],
                "release_date": "2025-05-14",
                "benchmark_scores": {"mmlu": 91.8, "human_eval": 95.2, "math": 85.6, "swe_bench": 70.3},
            },
        },
    },
    "google": {
        "provider": "Google",
        "models": {
            "gemini-2.5-pro": {
                "display_name": "Gemini 2.5 Pro",
                "category": "flagship",
                "context_window": 1048576,
                "input_price_per_1m": 1.25,
                "output_price_per_1m": 10.00,
                "capabilities": ["chat", "vision", "function_calling", "json_mode", "code_execution", "grounding"],
                "release_date": "2025-03-25",
                "benchmark_scores": {"mmlu": 90.1, "human_eval": 93.5, "math": 84.2, "swe_bench": 66.1},
            },
            "gemini-2.5-flash": {
                "display_name": "Gemini 2.5 Flash",
                "category": "cost_effective",
                "context_window": 1048576,
                "input_price_per_1m": 0.15,
                "output_price_per_1m": 0.60,
                "capabilities": ["chat", "vision", "function_calling", "json_mode", "grounding"],
                "release_date": "2025-05-20",
                "benchmark_scores": {"mmlu": 84.8, "human_eval": 89.1, "math": 76.3},
            },
            "gemini-2.0-flash": {
                "display_name": "Gemini 2.0 Flash",
                "category": "cost_effective",
                "context_window": 1048576,
                "input_price_per_1m": 0.10,
                "output_price_per_1m": 0.40,
                "capabilities": ["chat", "vision", "function_calling", "json_mode", "grounding"],
                "release_date": "2025-02-05",
                "benchmark_scores": {"mmlu": 81.5, "human_eval": 86.2, "math": 72.8},
            },
        },
    },
    "deepseek": {
        "provider": "DeepSeek",
        "models": {
            "deepseek-chat": {
                "display_name": "DeepSeek V3",
                "category": "cost_effective",
                "context_window": 65536,
                "input_price_per_1m": 0.27,
                "output_price_per_1m": 1.10,
                "capabilities": ["chat", "function_calling", "json_mode"],
                "release_date": "2025-01-20",
                "benchmark_scores": {"mmlu": 85.5, "human_eval": 87.8, "math": 78.9},
            },
            "deepseek-reasoner": {
                "display_name": "DeepSeek R1",
                "category": "reasoning",
                "context_window": 65536,
                "input_price_per_1m": 0.55,
                "output_price_per_1m": 2.19,
                "capabilities": ["chat", "reasoning", "function_calling"],
                "release_date": "2025-01-20",
                "benchmark_scores": {"mmlu": 87.1, "human_eval": 90.5, "math": 83.7},
            },
        },
    },
    "meta": {
        "provider": "Meta (Llama)",
        "models": {
            "llama-3.1-405b": {
                "display_name": "Llama 3.1 405B",
                "category": "open_source",
                "context_window": 128000,
                "input_price_per_1m": 0.00,
                "output_price_per_1m": 0.00,
                "capabilities": ["chat", "function_calling", "json_mode"],
                "release_date": "2024-07-23",
                "benchmark_scores": {"mmlu": 85.2, "human_eval": 86.5, "math": 73.8},
            },
            "llama-4-maverick": {
                "display_name": "Llama 4 Maverick",
                "category": "open_source",
                "context_window": 1048576,
                "input_price_per_1m": 0.00,
                "output_price_per_1m": 0.00,
                "capabilities": ["chat", "vision", "function_calling", "json_mode"],
                "release_date": "2025-04-05",
                "benchmark_scores": {"mmlu": 87.3, "human_eval": 89.1, "math": 78.4},
            },
        },
    },
    "qwen": {
        "provider": "Alibaba (Qwen)",
        "models": {
            "qwen3-235b-a22b": {
                "display_name": "Qwen3 235B",
                "category": "open_source",
                "context_window": 131072,
                "input_price_per_1m": 0.00,
                "output_price_per_1m": 0.00,
                "capabilities": ["chat", "reasoning", "function_calling", "json_mode"],
                "release_date": "2025-04-28",
                "benchmark_scores": {"mmlu": 86.7, "human_eval": 88.3, "math": 80.1},
            },
            "qwen3-32b": {
                "display_name": "Qwen3 32B",
                "category": "open_source",
                "context_window": 131072,
                "input_price_per_1m": 0.00,
                "output_price_per_1m": 0.00,
                "capabilities": ["chat", "reasoning", "function_calling", "json_mode"],
                "release_date": "2025-04-28",
                "benchmark_scores": {"mmlu": 82.1, "human_eval": 84.5, "math": 74.6},
            },
        },
    },
    "mistral": {
        "provider": "Mistral AI",
        "models": {
            "mistral-large-2411": {
                "display_name": "Mistral Large",
                "category": "flagship",
                "context_window": 128000,
                "input_price_per_1m": 2.00,
                "output_price_per_1m": 6.00,
                "capabilities": ["chat", "function_calling", "json_mode"],
                "release_date": "2024-11-25",
                "benchmark_scores": {"mmlu": 84.0, "human_eval": 87.3, "math": 75.2},
            },
            "codestral-latest": {
                "display_name": "Codestral",
                "category": "specialized",
                "context_window": 256000,
                "input_price_per_1m": 0.30,
                "output_price_per_1m": 0.90,
                "capabilities": ["chat", "code_generation", "function_calling", "json_mode"],
                "release_date": "2025-05-15",
                "benchmark_scores": {"human_eval": 91.2, "swe_bench": 58.3, "math": 72.1},
            },
        },
    },
}

# ─── Task Type Profiles ──────────────────────────────────────────────────────

TASK_PROFILES = {
    "general_chat": {
        "name": "General Chat / Q&A",
        "name_zh": "通用对话/问答",
        "weights": {"mmlu": 0.4, "human_eval": 0.3, "math": 0.1, "cost": 0.2},
        "required_capabilities": ["chat"],
        "preferred_capabilities": ["json_mode"],
    },
    "code_generation": {
        "name": "Code Generation",
        "name_zh": "代码生成",
        "weights": {"human_eval": 0.35, "swe_bench": 0.25, "mmlu": 0.1, "math": 0.1, "cost": 0.2},
        "required_capabilities": ["chat"],
        "preferred_capabilities": ["function_calling", "code_execution", "json_mode"],
    },
    "reasoning": {
        "name": "Complex Reasoning",
        "name_zh": "复杂推理",
        "weights": {"math": 0.35, "mmlu": 0.25, "human_eval": 0.2, "cost": 0.2},
        "required_capabilities": ["chat"],
        "preferred_capabilities": ["reasoning"],
    },
    "vision": {
        "name": "Vision / Image Understanding",
        "name_zh": "视觉/图像理解",
        "weights": {"mmlu": 0.3, "human_eval": 0.2, "cost": 0.3, "vision_quality": 0.2},
        "required_capabilities": ["chat", "vision"],
        "preferred_capabilities": ["function_calling"],
    },
    "long_context": {
        "name": "Long Context Processing",
        "name_zh": "长上下文处理",
        "weights": {"mmlu": 0.2, "human_eval": 0.2, "context_size": 0.3, "cost": 0.3},
        "required_capabilities": ["chat"],
        "preferred_capabilities": ["function_calling", "json_mode"],
    },
    "cost_sensitive": {
        "name": "Cost-Sensitive / High Volume",
        "name_zh": "成本敏感/高并发",
        "weights": {"cost": 0.5, "mmlu": 0.2, "human_eval": 0.2, "math": 0.1},
        "required_capabilities": ["chat"],
        "preferred_capabilities": ["json_mode"],
    },
    "function_calling": {
        "name": "Function Calling / Agent",
        "name_zh": "函数调用/智能体",
        "weights": {"mmlu": 0.2, "human_eval": 0.25, "swe_bench": 0.15, "cost": 0.2, "fc_quality": 0.2},
        "required_capabilities": ["chat", "function_calling"],
        "preferred_capabilities": ["json_mode", "code_execution"],
    },
}

# ─── Utility Functions ────────────────────────────────────────────────────────

def ensure_dirs():
    """Ensure configuration and data directories exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_json(filepath: Path, default=None):
    """Load JSON file with error handling."""
    try:
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    return default if default is not None else {}


def save_json(filepath: Path, data):
    """Save data to JSON file with error handling."""
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    except IOError as e:
        print(f"  [ERROR] Failed to save {filepath}: {e}")


def format_number(n):
    """Format large numbers with K/M suffix."""
    if n is None:
        return "N/A"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return f"{n:.1f}"


def format_price(price):
    """Format price per 1M tokens."""
    if price == 0:
        return "Free"
    return f"${price:.2f}"


def format_context(tokens):
    """Format context window size."""
    if tokens >= 1_000_000:
        return f"{tokens / 1_000_000:.1f}M"
    if tokens >= 1_000:
        return f"{tokens / 1_000:.0f}K"
    return str(tokens)


def get_all_models():
    """Get flattened list of all models with provider info."""
    models = []
    for provider_key, provider_data in MODELS_DB.items():
        for model_key, model_data in provider_data["models"].items():
            models.append({
                "id": model_key,
                "provider": provider_data["provider"],
                "provider_key": provider_key,
                **model_data,
            })
    return models


def check_api_endpoint(url: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
    """
    Check API endpoint availability and measure latency.
    Returns dict with status, latency_ms, and error info.
    """
    result = {
        "url": url,
        "status": "unknown",
        "latency_ms": None,
        "error": None,
        "timestamp": datetime.now().isoformat(),
    }
    try:
        ctx = ssl.create_default_context()
        req = Request(url, method="HEAD", headers={"User-Agent": "ModelPulse-CLI/1.0"})
        start = time.monotonic()
        resp = urlopen(req, timeout=timeout, context=ctx)
        elapsed = (time.monotonic() - start) * 1000
        result["status"] = "ok" if resp.status < 400 else "error"
        result["latency_ms"] = round(elapsed, 1)
        result["http_status"] = resp.status
    except HTTPError as e:
        result["status"] = "error"
        result["http_status"] = e.code
        result["error"] = str(e.reason)
    except URLError as e:
        result["status"] = "error"
        result["error"] = str(e.reason)
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    return result


def compute_score(model: dict, task_profile: dict) -> float:
    """
    Compute recommendation score for a model given a task profile.
    Score is 0-100, higher is better.
    """
    weights = task_profile["weights"]
    required = task_profile["required_capabilities"]
    preferred = task_profile.get("preferred_capabilities", [])

    # Check required capabilities
    caps = model.get("capabilities", [])
    for cap in required:
        if cap not in caps:
            return 0.0

    scores = {}
    benchmarks = model.get("benchmark_scores", {})

    # Benchmark scores (normalized to 0-100)
    for key in ["mmlu", "human_eval", "math", "swe_bench"]:
        if key in weights and key in benchmarks:
            scores[key] = benchmarks[key]

    # Cost score (inverse - lower is better, normalized)
    if "cost" in weights:
        total_cost = model.get("input_price_per_1m", 0) + model.get("output_price_per_1m", 0)
        # Free models get max cost score, paid models scale inversely
        if total_cost == 0:
            scores["cost"] = 100.0
        else:
            scores["cost"] = max(0, 100 - (total_cost / 0.85) * 100)  # $0.85 as reference max

    # Context size score
    if "context_size" in weights:
        ctx = model.get("context_window", 0)
        scores["context_size"] = min(100, (ctx / 1_048_576) * 100)  # 1M as reference

    # Capability bonus
    pref_count = sum(1 for cap in preferred if cap in caps)
    if preferred:
        cap_bonus = (pref_count / len(preferred)) * 5  # up to 5 bonus points

    # Weighted score
    total_weight = 0
    weighted_sum = 0
    for key, weight in weights.items():
        if key in scores:
            weighted_sum += scores[key] * weight
            total_weight += weight

    base_score = (weighted_sum / total_weight) if total_weight > 0 else 0

    return min(100, base_score + cap_bonus)


# ─── Core Commands ────────────────────────────────────────────────────────────

def cmd_list(args):
    """List all tracked AI models with details."""
    models = get_all_models()
    provider_filter = args.provider.lower() if args.provider else None
    category_filter = args.category.lower() if args.category else None
    sort_by = args.sort

    if provider_filter:
        models = [m for m in models if provider_filter in m["provider"].lower()
                  or provider_filter in m["provider_key"].lower()]
    if category_filter:
        models = [m for m in models if category_filter == m.get("category", "").lower()]

    if sort_by == "price":
        models.sort(key=lambda m: m.get("input_price_per_1m", 0) + m.get("output_price_per_1m", 0))
    elif sort_by == "context":
        models.sort(key=lambda m: m.get("context_window", 0), reverse=True)
    elif sort_by == "name":
        models.sort(key=lambda m: m["display_name"].lower())
    elif sort_by == "mmlu":
        models.sort(key=lambda m: m.get("benchmark_scores", {}).get("mmlu", 0), reverse=True)
    elif sort_by == "math":
        models.sort(key=lambda m: m.get("benchmark_scores", {}).get("math", 0), reverse=True)

    # Display
    print(f"\n{'='*100}")
    print(f"  {APP_NAME} - AI Model Registry  |  {len(models)} models tracked  |  Updated: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"{'='*100}")
    print(f"  {'Model':<25} {'Provider':<16} {'Category':<14} {'Context':<10} {'In$/1M':<10} {'Out$/1M':<10} {'MMLU':<7} {'Math':<7}")
    print(f"  {'-'*25} {'-'*16} {'-'*14} {'-'*10} {'-'*10} {'-'*10} {'-'*7} {'-'*7}")

    for m in models:
        bm = m.get("benchmark_scores", {})
        mmlu = f"{bm.get('mmlu', 0):.1f}" if bm.get('mmlu') else "N/A"
        math_s = f"{bm.get('math', 0):.1f}" if bm.get('math') else "N/A"
        cat_display = m.get("category", "").replace("_", "-").title()
        print(f"  {m['display_name']:<25} {m['provider']:<16} {cat_display:<14} "
              f"{format_context(m.get('context_window', 0)):<10} "
              f"{format_price(m.get('input_price_per_1m', 0)):<10} "
              f"{format_price(m.get('output_price_per_1m', 0)):<10} "
              f"{mmlu:<7} {math_s:<7}")

    print(f"{'='*100}\n")


def cmd_monitor(args):
    """Monitor API endpoint status for configured providers."""
    print(f"\n  {APP_NAME} - API Endpoint Monitor")
    print(f"  Checking endpoint availability...\n")

    endpoints = {
        "OpenAI": "https://api.openai.com/v1/models",
        "Anthropic": "https://api.anthropic.com/v1/messages",
        "Google AI": "https://generativelanguage.googleapis.com/v1beta/models",
        "DeepSeek": "https://api.deepseek.com/v1/models",
        "Mistral": "https://api.mistral.ai/v1/models",
    }

    results = []
    for name, url in endpoints.items():
        print(f"  Checking {name}...", end=" ", flush=True)
        result = check_api_endpoint(url, timeout=args.timeout)
        results.append({"provider": name, **result})

        if result["status"] == "ok":
            print(f"[OK] {result['latency_ms']:.0f}ms")
        else:
            err = result.get("error", "Unknown error")[:50]
            print(f"[FAIL] {err}")

    # Save results
    ensure_dirs()
    history = load_json(HISTORY_FILE, [])
    record = {
        "timestamp": datetime.now().isoformat(),
        "type": "monitor",
        "results": results,
    }
    history.append(record)
    # Trim old records
    cutoff = (datetime.now() - timedelta(days=MAX_HISTORY_DAYS)).isoformat()
    history = [r for r in history if r.get("timestamp", "") > cutoff]
    save_json(HISTORY_FILE, history)

    # Summary
    ok_count = sum(1 for r in results if r["status"] == "ok")
    print(f"\n  Summary: {ok_count}/{len(results)} endpoints reachable")
    print(f"  Results saved to {HISTORY_FILE}\n")


def cmd_recommend(args):
    """Recommend best model for a given task type."""
    task_key = args.task.lower().replace("-", "_")
    if task_key not in TASK_PROFILES:
        print(f"\n  [ERROR] Unknown task type: {args.task}")
        print(f"  Available tasks: {', '.join(TASK_PROFILES.keys())}\n")
        return

    profile = TASK_PROFILES[task_key]
    models = get_all_models()

    # Filter by API key availability if specified
    if args.api_key:
        # Only show models from providers with configured API keys
        config = load_json(CONFIG_FILE, {})
        api_keys = config.get("api_keys", {})
        available_providers = [k for k, v in api_keys.items() if v]
        if available_providers:
            models = [m for m in models if m["provider_key"] in available_providers]

    # Score all models
    scored = []
    for m in models:
        score = compute_score(m, profile)
        if score > 0:
            scored.append((m, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    top_n = min(args.top, len(scored))

    # Display
    print(f"\n{'='*90}")
    print(f"  {APP_NAME} - Smart Recommendation")
    print(f"  Task: {profile['name']} ({profile.get('name_zh', '')})")
    print(f"  Evaluated: {len(scored)} models  |  Showing top {top_n}")
    print(f"{'='*90}")

    for i, (m, score) in enumerate(scored[:top_n], 1):
        bm = m.get("benchmark_scores", {})
        total_cost = m.get("input_price_per_1m", 0) + m.get("output_price_per_1m", 0)
        caps = ", ".join(m.get("capabilities", [])[:4])
        if len(m.get("capabilities", [])) > 4:
            caps += f" +{len(m['capabilities']) - 4} more"

        medal = ["#1", "#2", "#3"][i-1] if i <= 3 else f"#{i}"
        print(f"\n  {medal}  {m['display_name']}  ({m['provider']})  Score: {score:.1f}/100")
        print(f"      Category: {m.get('category', '').replace('_', '-').title()}  |  "
              f"Context: {format_context(m.get('context_window', 0))}  |  "
              f"Cost: {format_price(m.get('input_price_per_1m', 0))} in / {format_price(m.get('output_price_per_1m', 0))} out")
        print(f"      MMLU: {bm.get('mmlu', 'N/A')}  |  "
              f"HumanEval: {bm.get('human_eval', 'N/A')}  |  "
              f"Math: {bm.get('math', 'N/A')}  |  "
              f"SWE-Bench: {bm.get('swe_bench', 'N/A')}")
        print(f"      Capabilities: {caps}")

    print(f"\n{'='*90}\n")

    # Save recommendation
    ensure_dirs()
    history = load_json(HISTORY_FILE, [])
    record = {
        "timestamp": datetime.now().isoformat(),
        "type": "recommend",
        "task": task_key,
        "results": [{"model": m["display_name"], "provider": m["provider"], "score": round(s, 2)} for m, s in scored[:top_n]],
    }
    history.append(record)
    cutoff = (datetime.now() - timedelta(days=MAX_HISTORY_DAYS)).isoformat()
    history = [r for r in history if r.get("timestamp", "") > cutoff]
    save_json(HISTORY_FILE, history)


def cmd_compare(args):
    """Compare two or more models side by side."""
    models = get_all_models()
    model_names = [n.strip() for n in args.models.split(",")]

    selected = []
    for name in model_names:
        found = [m for m in models if name.lower() in m["display_name"].lower() or name.lower() in m["id"].lower()]
        if found:
            selected.append(found[0])
        else:
            print(f"  [WARN] Model not found: {name}")

    if len(selected) < 2:
        print(f"\n  [ERROR] Need at least 2 models to compare. Found: {len(selected)}\n")
        return

    # Display comparison table
    metrics = ["mmlu", "human_eval", "math", "swe_bench"]
    print(f"\n{'='*100}")
    print(f"  {APP_NAME} - Model Comparison")
    print(f"{'='*100}")

    # Header
    header = f"  {'Metric':<20}"
    for m in selected:
        header += f" {m['display_name']:<22}"
    print(header)
    print(f"  {'-'*20}" + f" {'-'*22}" * len(selected))

    # Provider & Category
    print(f"  {'Provider':<20}" + "".join(f" {m['provider']:<22}" for m in selected))
    print(f"  {'Category':<20}" + "".join(f" {m.get('category','').replace('_','-').title():<22}" for m in selected))
    print(f"  {'Context Window':<20}" + "".join(f" {format_context(m.get('context_window',0)):<22}" for m in selected))
    print(f"  {'Input Price/1M':<20}" + "".join(f" {format_price(m.get('input_price_per_1m',0)):<22}" for m in selected))
    print(f"  {'Output Price/1M':<20}" + "".join(f" {format_price(m.get('output_price_per_1m',0)):<22}" for m in selected))
    print(f"  {'-'*20}" + f" {'-'*22}" * len(selected))

    # Benchmark scores
    for metric in metrics:
        row = f"  {metric.upper():<20}"
        for m in selected:
            val = m.get("benchmark_scores", {}).get(metric)
            row += f" {f'{val:.1f}':<22}" if val else f" {'N/A':<22}"
        print(row)

    # Capabilities
    print(f"  {'-'*20}" + f" {'-'*22}" * len(selected))
    print(f"  {'Capabilities':<20}" + "".join(f" {', '.join(m.get('capabilities',[])[:3]):<22}" for m in selected))

    # Find best per metric
    print(f"\n  Best per metric:")
    for metric in metrics:
        best = max(selected, key=lambda m: m.get("benchmark_scores", {}).get(metric, 0))
        val = best.get("benchmark_scores", {}).get(metric, 0)
        if val:
            print(f"    {metric.upper()}: {best['display_name']} ({val})")

    print(f"\n{'='*100}\n")


def cmd_pricing(args):
    """Show pricing comparison across all models."""
    models = get_all_models()

    if args.provider:
        models = [m for m in models if args.provider.lower() in m["provider"].lower()]

    # Sort by total cost
    models.sort(key=lambda m: m.get("input_price_per_1m", 0) + m.get("output_price_per_1m", 0))

    print(f"\n{'='*95}")
    print(f"  {APP_NAME} - Pricing Dashboard")
    print(f"{'='*95}")
    print(f"  {'Model':<25} {'Provider':<16} {'In $/1M':<12} {'Out $/1M':<12} {'Total $/1M':<12} {'Context':<10}")
    print(f"  {'-'*25} {'-'*16} {'-'*12} {'-'*12} {'-'*12} {'-'*10}")

    for m in models:
        in_p = m.get("input_price_per_1m", 0)
        out_p = m.get("output_price_per_1m", 0)
        total = in_p + out_p
        print(f"  {m['display_name']:<25} {m['provider']:<16} "
              f"{format_price(in_p):<12} {format_price(out_p):<12} {format_price(total):<12} "
              f"{format_context(m.get('context_window', 0)):<10}")

    # Cost analysis
    paid_models = [m for m in models if m.get("input_price_per_1m", 0) > 0]
    if paid_models:
        cheapest = paid_models[0]
        print(f"\n  Cheapest: {cheapest['display_name']} ({cheapest['provider']}) - "
              f"${cheapest.get('input_price_per_1m', 0) + cheapest.get('output_price_per_1m', 0):.2f}/1M total")

        expensive = paid_models[-1]
        print(f"  Most Expensive: {expensive['display_name']} ({expensive['provider']}) - "
              f"${expensive.get('input_price_per_1m', 0) + expensive.get('output_price_per_1m', 0):.2f}/1M total")

        free_models = [m for m in models if m.get("input_price_per_1m", 0) == 0]
        if free_models:
            print(f"  Free (Open Source): {', '.join(m['display_name'] for m in free_models)}")

    print(f"\n{'='*95}\n")


def cmd_export(args):
    """Export model data to various formats."""
    models = get_all_models()
    fmt = args.format.lower()

    if fmt == "json":
        filepath = Path(args.output) if args.output else Path("modelpulse_export.json")
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "version": VERSION,
            "models": models,
            "task_profiles": TASK_PROFILES,
        }
        save_json(filepath, export_data)
        print(f"  Exported {len(models)} models to {filepath}")

    elif fmt == "csv":
        filepath = Path(args.output) if args.output else Path("modelpulse_export.csv")
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Model", "Provider", "Category", "Context_Window",
                "Input_Price_1M", "Output_Price_1M", "MMLU", "HumanEval",
                "Math", "SWE_Bench", "Capabilities", "Release_Date"
            ])
            for m in models:
                bm = m.get("benchmark_scores", {})
                writer.writerow([
                    m["display_name"], m["provider"], m.get("category", ""),
                    m.get("context_window", 0),
                    m.get("input_price_per_1m", 0), m.get("output_price_per_1m", 0),
                    bm.get("mmlu", ""), bm.get("human_eval", ""),
                    bm.get("math", ""), bm.get("swe_bench", ""),
                    ";".join(m.get("capabilities", [])),
                    m.get("release_date", ""),
                ])
        print(f"  Exported {len(models)} models to {filepath}")

    elif fmt == "markdown":
        filepath = Path(args.output) if args.output else Path("modelpulse_export.md")
        lines = [
            f"# {APP_NAME} - Model Database Export",
            f"",
            f"> Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}  |  Version: {VERSION}  |  Models: {len(models)}",
            f"",
            f"| Model | Provider | Category | Context | In $/1M | Out $/1M | MMLU | Math |",
            f"|-------|----------|----------|---------|---------|----------|------|------|",
        ]
        for m in models:
            bm = m.get("benchmark_scores", {})
            lines.append(
                f"| {m['display_name']} | {m['provider']} | "
                f"{m.get('category','').replace('_','-').title()} | "
                f"{format_context(m.get('context_window',0))} | "
                f"{format_price(m.get('input_price_per_1m',0))} | "
                f"{format_price(m.get('output_price_per_1m',0))} | "
                f"{bm.get('mmlu', 'N/A')} | {bm.get('math', 'N/A')} |"
            )
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"  Exported {len(models)} models to {filepath}")

    else:
        print(f"  [ERROR] Unsupported format: {fmt}. Use json, csv, or markdown.")


def cmd_history(args):
    """Show historical monitoring and recommendation data."""
    ensure_dirs()
    history = load_json(HISTORY_FILE, [])

    if not history:
        print(f"\n  No history data found. Run 'modelpulse monitor' or 'modelpulse recommend' first.\n")
        return

    # Filter by type
    hist_type = args.type.lower() if args.type else None
    if hist_type:
        history = [r for r in history if r.get("type") == hist_type]

    limit = args.limit or len(history)
    history = history[-limit:]

    print(f"\n{'='*80}")
    print(f"  {APP_NAME} - History  |  {len(history)} records")
    print(f"{'='*80}")

    for record in reversed(history):
        ts = record.get("timestamp", "unknown")
        rtype = record.get("type", "unknown")
        print(f"\n  [{ts}]  Type: {rtype}")

        if rtype == "monitor":
            for r in record.get("results", []):
                status = "[OK]" if r.get("status") == "ok" else "[FAIL]"
                latency = f" {r.get('latency_ms', 0):.0f}ms" if r.get("latency_ms") else ""
                print(f"    {status} {r.get('provider', '?')}{latency}")
        elif rtype == "recommend":
            task = record.get("task", "?")
            print(f"    Task: {task}")
            for r in record.get("results", []):
                print(f"      {r.get('model', '?')} ({r.get('provider', '?')}) - Score: {r.get('score', 0)}")

    print(f"\n{'='*80}\n")


def cmd_config(args):
    """Manage configuration."""
    ensure_dirs()

    if args.show:
        config = load_json(CONFIG_FILE, {"api_keys": {}, "preferences": {}})
        print(f"\n  Configuration ({CONFIG_FILE}):")
        print(json.dumps(config, indent=2, ensure_ascii=False))
        print()
        return

    if args.set_key:
        parts = args.set_key.split("=", 1)
        if len(parts) == 2:
            config = load_json(CONFIG_FILE, {"api_keys": {}, "preferences": {}})
            config.setdefault("api_keys", {})[parts[0].strip()] = parts[1].strip()
            save_json(CONFIG_FILE, config)
            print(f"  Set API key for '{parts[0].strip()}'")
        else:
            print("  Usage: modelpulse config --set-key PROVIDER=your_api_key")
        return

    print(f"\n  Configuration file: {CONFIG_FILE}")
    print(f"  Data directory: {DATA_DIR}")
    print(f"  History file: {HISTORY_FILE}")
    print(f"\n  Commands:")
    print(f"    modelpulse config --show          Show current config")
    print(f"    modelpulse config --set-key P=K   Set API key for provider")
    print()


def cmd_tasks(args):
    """List available task types for recommendation."""
    print(f"\n{'='*70}")
    print(f"  {APP_NAME} - Available Task Types")
    print(f"{'='*70}")

    for key, profile in TASK_PROFILES.items():
        print(f"\n  {key}")
        print(f"    {profile['name']} ({profile.get('name_zh', '')})")
        print(f"    Required: {', '.join(profile['required_capabilities'])}")
        print(f"    Preferred: {', '.join(profile.get('preferred_capabilities', []))}")

    print(f"\n  Usage: modelpulse recommend --task <task_type>\n")
    print(f"{'='*70}\n")


# ─── Main Entry Point ────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="modelpulse",
        description=f"{APP_NAME} v{VERSION} - Lightweight Terminal AI Model Real-time Monitoring & Intelligent Recommendation Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  modelpulse list                          List all models
  modelpulse list --provider openai        Filter by provider
  modelpulse list --sort price             Sort by price
  modelpulse monitor                       Check API endpoint status
  modelpulse recommend --task code_gen     Get model recommendation
  modelpulse compare "gpt-4o,claude-sonnet-4-20250514"  Compare models
  modelpulse pricing                       Show pricing dashboard
  modelpulse export --format csv           Export to CSV
  modelpulse history                       View history
  modelpulse tasks                         List task types
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # list
    p_list = subparsers.add_parser("list", help="List all tracked AI models")
    p_list.add_argument("--provider", "-p", help="Filter by provider name")
    p_list.add_argument("--category", "-c", help="Filter by category")
    p_list.add_argument("--sort", "-s", choices=["name", "price", "context", "mmlu", "math"], default="name", help="Sort models")

    # monitor
    p_monitor = subparsers.add_parser("monitor", help="Monitor API endpoint status")
    p_monitor.add_argument("--timeout", "-t", type=int, default=DEFAULT_TIMEOUT, help="Request timeout in seconds")

    # recommend
    p_recommend = subparsers.add_parser("recommend", help="Recommend best model for a task")
    p_recommend.add_argument("--task", "-t", required=True, help="Task type (use 'tasks' to list)")
    p_recommend.add_argument("--top", "-n", type=int, default=5, help="Number of recommendations")
    p_recommend.add_argument("--api-key", action="store_true", help="Only recommend from configured providers")

    # compare
    p_compare = subparsers.add_parser("compare", help="Compare models side by side")
    p_compare.add_argument("models", help="Comma-separated model names to compare")

    # pricing
    p_pricing = subparsers.add_parser("pricing", help="Show pricing comparison")
    p_pricing.add_argument("--provider", "-p", help="Filter by provider")

    # export
    p_export = subparsers.add_parser("export", help="Export model data")
    p_export.add_argument("--format", "-f", choices=["json", "csv", "markdown"], default="json", help="Export format")
    p_export.add_argument("--output", "-o", help="Output file path")

    # history
    p_history = subparsers.add_parser("history", help="View historical data")
    p_history.add_argument("--type", "-t", choices=["monitor", "recommend"], help="Filter by type")
    p_history.add_argument("--limit", "-n", type=int, help="Number of records to show")

    # config
    p_config = subparsers.add_parser("config", help="Manage configuration")
    p_config.add_argument("--show", action="store_true", help="Show current config")
    p_config.add_argument("--set-key", metavar="PROVIDER=KEY", help="Set API key for a provider")

    # tasks
    subparsers.add_parser("tasks", help="List available task types")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    commands = {
        "list": cmd_list,
        "monitor": cmd_monitor,
        "recommend": cmd_recommend,
        "compare": cmd_compare,
        "pricing": cmd_pricing,
        "export": cmd_export,
        "history": cmd_history,
        "config": cmd_config,
        "tasks": cmd_tasks,
    }

    cmd_func = commands.get(args.command)
    if cmd_func:
        cmd_func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

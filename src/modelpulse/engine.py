"""
ModelPulse-CLI - Core Engine Module
Provides model scoring, comparison, and analysis logic.
"""

import statistics
from datetime import datetime
from typing import Optional


class ModelScorer:
    """Advanced model scoring engine with multiple strategies."""

    def __init__(self, weights: Optional[dict] = None):
        self.weights = weights or {}

    def score(self, model: dict, profile: dict) -> dict:
        """
        Compute detailed scoring breakdown for a model.
        Returns dict with total score and per-category breakdowns.
        """
        weights = profile.get("weights", {})
        required = profile.get("required_capabilities", [])
        preferred = profile.get("preferred_capabilities", [])
        caps = model.get("capabilities", [])

        # Check required capabilities
        for cap in required:
            if cap not in caps:
                return {"total": 0.0, "breakdown": {}, "disqualified": True, "reason": f"Missing: {cap}"}

        breakdown = {}
        benchmarks = model.get("benchmark_scores", {})

        # Benchmark scores
        for key in ["mmlu", "human_eval", "math", "swe_bench"]:
            if key in weights:
                val = benchmarks.get(key, 0)
                breakdown[key] = {"value": val, "weight": weights[key], "weighted": val * weights[key]}

        # Cost score
        if "cost" in weights:
            total_cost = model.get("input_price_per_1m", 0) + model.get("output_price_per_1m", 0)
            cost_score = 100.0 if total_cost == 0 else max(0, 100 - (total_cost / 0.85) * 100)
            breakdown["cost"] = {"value": cost_score, "weight": weights["cost"], "weighted": cost_score * weights["cost"], "raw_cost": total_cost}

        # Context size
        if "context_size" in weights:
            ctx = model.get("context_window", 0)
            ctx_score = min(100, (ctx / 1_048_576) * 100)
            breakdown["context_size"] = {"value": ctx_score, "weight": weights["context_size"], "weighted": ctx_score * weights["context_size"], "raw_context": ctx}

        # Capability bonus
        pref_count = sum(1 for cap in preferred if cap in caps)
        cap_bonus = (pref_count / len(preferred)) * 5 if preferred else 0

        total_weight = sum(b["weight"] for b in breakdown.values())
        weighted_sum = sum(b["weighted"] for b in breakdown.values())
        base_score = (weighted_sum / total_weight) if total_weight > 0 else 0
        total = min(100, base_score + cap_bonus)

        return {
            "total": round(total, 2),
            "breakdown": breakdown,
            "disqualified": False,
            "capability_bonus": round(cap_bonus, 2),
            "capabilities_match": f"{pref_count}/{len(preferred)}",
        }


class CostAnalyzer:
    """Analyze and compare model costs."""

    @staticmethod
    def estimate_cost(model: dict, input_tokens: int, output_tokens: int) -> dict:
        """Estimate total API cost for a given usage pattern."""
        in_cost = (input_tokens / 1_000_000) * model.get("input_price_per_1m", 0)
        out_cost = (output_tokens / 1_000_000) * model.get("output_price_per_1m", 0)
        return {
            "input_cost": round(in_cost, 6),
            "output_cost": round(out_cost, 6),
            "total_cost": round(in_cost + out_cost, 6),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        }

    @staticmethod
    def find_cheapest(models: list, input_tokens: int = 100000, output_tokens: int = 10000) -> list:
        """Find cheapest models for given usage pattern."""
        results = []
        for m in models:
            cost = CostAnalyzer.estimate_cost(m, input_tokens, output_tokens)
            results.append({"model": m["display_name"], "provider": m["provider"], **cost})
        results.sort(key=lambda x: x["total_cost"])
        return results

    @staticmethod
    def cost_comparison_table(models: list, scenarios: list = None) -> list:
        """Generate cost comparison across multiple usage scenarios."""
        if scenarios is None:
            scenarios = [
                {"name": "Light (10K in / 1K out)", "input": 10000, "output": 1000},
                {"name": "Medium (100K in / 10K out)", "input": 100000, "output": 10000},
                {"name": "Heavy (1M in / 100K out)", "input": 1000000, "output": 100000},
            ]

        results = []
        for m in models:
            row = {"model": m["display_name"], "provider": m["provider"]}
            for scenario in scenarios:
                cost = CostAnalyzer.estimate_cost(m, scenario["input"], scenario["output"])
                row[scenario["name"]] = cost["total_cost"]
            results.append(row)
        return results


class TrendTracker:
    """Track model performance and pricing trends over time."""

    def __init__(self, history: list = None):
        self.history = history or []

    def add_record(self, record: dict):
        """Add a new monitoring/recommendation record."""
        record["timestamp"] = datetime.now().isoformat()
        self.history.append(record)

    def get_latency_trend(self, provider: str, hours: int = 24) -> dict:
        """Get latency trend for a specific provider."""
        from datetime import timedelta
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
        records = [
            r for r in self.history
            if r.get("type") == "monitor" and r.get("timestamp", "") > cutoff
        ]

        latencies = []
        for r in records:
            for result in r.get("results", []):
                if result.get("provider") == provider and result.get("latency_ms"):
                    latencies.append(result["latency_ms"])

        if not latencies:
            return {"provider": provider, "status": "no_data", "hours": hours}

        return {
            "provider": provider,
            "status": "ok",
            "hours": hours,
            "samples": len(latencies),
            "avg_ms": round(statistics.mean(latencies), 1),
            "min_ms": round(min(latencies), 1),
            "max_ms": round(max(latencies), 1),
            "p50_ms": round(sorted(latencies)[len(latencies) // 2], 1),
            "stdev_ms": round(statistics.stdev(latencies), 1) if len(latencies) > 1 else 0,
        }

    def get_uptime_stats(self, hours: int = 24) -> dict:
        """Get uptime statistics across all providers."""
        from datetime import timedelta
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
        records = [
            r for r in self.history
            if r.get("type") == "monitor" and r.get("timestamp", "") > cutoff
        ]

        provider_stats = {}
        for r in records:
            for result in r.get("results", []):
                p = result.get("provider", "unknown")
                if p not in provider_stats:
                    provider_stats[p] = {"ok": 0, "fail": 0}
                if result.get("status") == "ok":
                    provider_stats[p]["ok"] += 1
                else:
                    provider_stats[p]["fail"] += 1

        return {
            "hours": hours,
            "providers": provider_stats,
        }

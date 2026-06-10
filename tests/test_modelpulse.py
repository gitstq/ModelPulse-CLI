"""
ModelPulse-CLI - Test Suite
Unit tests for core functionality.
"""

import unittest
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from modelpulse.cli import (
    get_all_models, compute_score, format_number, format_price,
    format_context, check_api_endpoint, TASK_PROFILES, MODELS_DB,
)
from modelpulse.engine import ModelScorer, CostAnalyzer, TrendTracker
from modelpulse.models import ModelInfo, BenchmarkScores, EndpointCheckResult


class TestModelDatabase(unittest.TestCase):
    """Test model database integrity."""

    def test_models_db_not_empty(self):
        self.assertTrue(len(MODELS_DB) > 0, "Model database should not be empty")

    def test_all_providers_have_models(self):
        for provider_key, provider_data in MODELS_DB.items():
            self.assertIn("models", provider_data)
            self.assertTrue(len(provider_data["models"]) > 0,
                            f"Provider {provider_key} should have at least one model")

    def test_model_required_fields(self):
        for provider_key, provider_data in MODELS_DB.items():
            for model_key, model_data in provider_data["models"].items():
                self.assertIn("display_name", model_data, f"{provider_key}/{model_key} missing display_name")
                self.assertIn("category", model_data, f"{provider_key}/{model_key} missing category")
                self.assertIn("context_window", model_data, f"{provider_key}/{model_key} missing context_window")
                self.assertIn("capabilities", model_data, f"{provider_key}/{model_key} missing capabilities")

    def test_get_all_models(self):
        models = get_all_models()
        self.assertTrue(len(models) > 0)
        for m in models:
            self.assertIn("id", m)
            self.assertIn("provider", m)
            self.assertIn("display_name", m)


class TestScoring(unittest.TestCase):
    """Test model scoring engine."""

    def test_compute_score_returns_number(self):
        models = get_all_models()
        profile = TASK_PROFILES["general_chat"]
        for m in models[:5]:
            score = compute_score(m, profile)
            self.assertIsInstance(score, float)
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 100)

    def test_compute_score_zero_for_missing_capability(self):
        model = {
            "capabilities": ["chat"],
            "benchmark_scores": {"mmlu": 90, "human_eval": 90, "math": 90},
            "input_price_per_1m": 2.0,
            "output_price_per_1m": 8.0,
        }
        # Vision task requires "vision" capability
        profile = TASK_PROFILES["vision"]
        score = compute_score(model, profile)
        self.assertEqual(score, 0.0)

    def test_compute_score_positive_for_valid_model(self):
        model = {
            "capabilities": ["chat", "vision", "function_calling", "json_mode"],
            "benchmark_scores": {"mmlu": 88.7, "human_eval": 90.2, "math": 76.6},
            "input_price_per_1m": 2.50,
            "output_price_per_1m": 10.00,
        }
        profile = TASK_PROFILES["general_chat"]
        score = compute_score(model, profile)
        self.assertGreater(score, 0)

    def test_free_model_gets_high_cost_score(self):
        free_model = {
            "capabilities": ["chat", "json_mode"],
            "benchmark_scores": {"mmlu": 80, "human_eval": 80, "math": 70},
            "input_price_per_1m": 0,
            "output_price_per_1m": 0,
        }
        paid_model = {
            "capabilities": ["chat", "json_mode"],
            "benchmark_scores": {"mmlu": 80, "human_eval": 80, "math": 70},
            "input_price_per_1m": 10.0,
            "output_price_per_1m": 40.0,
        }
        profile = TASK_PROFILES["cost_sensitive"]
        free_score = compute_score(free_model, profile)
        paid_score = compute_score(paid_model, profile)
        self.assertGreater(free_score, paid_score)


class TestModelScorer(unittest.TestCase):
    """Test advanced ModelScorer class."""

    def test_detailed_scoring(self):
        scorer = ModelScorer()
        model = {
            "capabilities": ["chat", "function_calling", "json_mode", "code_execution"],
            "benchmark_scores": {"mmlu": 90, "human_eval": 92, "math": 80, "swe_bench": 60},
            "input_price_per_1m": 2.0,
            "output_price_per_1m": 8.0,
        }
        profile = TASK_PROFILES["code_generation"]
        result = scorer.score(model, profile)
        self.assertIn("total", result)
        self.assertIn("breakdown", result)
        self.assertFalse(result.get("disqualified", True))
        self.assertGreater(result["total"], 0)

    def test_disqualified_model(self):
        scorer = ModelScorer()
        model = {
            "capabilities": ["chat"],  # Missing vision
            "benchmark_scores": {"mmlu": 95},
        }
        profile = TASK_PROFILES["vision"]
        result = scorer.score(model, profile)
        self.assertTrue(result.get("disqualified", False))
        self.assertEqual(result["total"], 0)


class TestCostAnalyzer(unittest.TestCase):
    """Test cost analysis."""

    def test_estimate_cost_free_model(self):
        model = {"input_price_per_1m": 0, "output_price_per_1m": 0}
        result = CostAnalyzer.estimate_cost(model, 100000, 10000)
        self.assertEqual(result["total_cost"], 0)

    def test_estimate_cost_paid_model(self):
        model = {"input_price_per_1m": 2.0, "output_price_per_1m": 8.0}
        result = CostAnalyzer.estimate_cost(model, 100000, 10000)
        self.assertAlmostEqual(result["input_cost"], 0.2, places=4)
        self.assertAlmostEqual(result["output_cost"], 0.08, places=4)
        self.assertAlmostEqual(result["total_cost"], 0.28, places=4)

    def test_find_cheapest(self):
        models = [
            {"display_name": "Cheap", "provider": "Test", "input_price_per_1m": 0.1, "output_price_per_1m": 0.3},
            {"display_name": "Expensive", "provider": "Test", "input_price_per_1m": 10.0, "output_price_per_1m": 40.0},
        ]
        results = CostAnalyzer.find_cheapest(models, 100000, 10000)
        self.assertEqual(results[0]["model"], "Cheap")

    def test_cost_comparison_table(self):
        models = get_all_models()[:3]
        table = CostAnalyzer.cost_comparison_table(models)
        self.assertEqual(len(table), 3)
        for row in table:
            self.assertIn("model", row)
            self.assertIn("provider", row)


class TestFormatting(unittest.TestCase):
    """Test formatting utilities."""

    def test_format_number(self):
        self.assertEqual(format_number(1500), "1.5K")
        self.assertEqual(format_number(2500000), "2.5M")
        self.assertEqual(format_number(42), "42.0")
        self.assertEqual(format_number(None), "N/A")

    def test_format_price(self):
        self.assertEqual(format_price(0), "Free")
        self.assertEqual(format_price(2.50), "$2.50")
        self.assertEqual(format_price(0.15), "$0.15")

    def test_format_context(self):
        self.assertEqual(format_context(128000), "128K")
        self.assertEqual(format_context(1048576), "1.0M")
        self.assertEqual(format_context(65536), "66K")


class TestTaskProfiles(unittest.TestCase):
    """Test task profile definitions."""

    def test_all_profiles_have_required_fields(self):
        for key, profile in TASK_PROFILES.items():
            self.assertIn("name", profile)
            self.assertIn("weights", profile)
            self.assertIn("required_capabilities", profile)
            self.assertIsInstance(profile["weights"], dict)
            self.assertGreater(len(profile["weights"]), 0)

    def test_weights_sum_reasonable(self):
        for key, profile in TASK_PROFILES.items():
            total = sum(profile["weights"].values())
            # Weights should sum to roughly 1.0 (with some flexibility for bonus)
            self.assertLessEqual(total, 1.5, f"{key} weights sum too high: {total}")


class TestTrendTracker(unittest.TestCase):
    """Test trend tracking."""

    def test_empty_tracker(self):
        tracker = TrendTracker()
        trend = tracker.get_latency_trend("OpenAI")
        self.assertEqual(trend["status"], "no_data")

    def test_add_record(self):
        tracker = TrendTracker()
        tracker.add_record({"type": "monitor", "results": [
            {"provider": "OpenAI", "status": "ok", "latency_ms": 150}
        ]})
        self.assertEqual(len(tracker.history), 1)

    def test_uptime_stats(self):
        tracker = TrendTracker()
        tracker.add_record({"type": "monitor", "results": [
            {"provider": "OpenAI", "status": "ok"},
            {"provider": "Anthropic", "status": "error"},
        ]})
        stats = tracker.get_uptime_stats(hours=1)
        self.assertIn("providers", stats)
        self.assertIn("OpenAI", stats["providers"])


class TestDataModels(unittest.TestCase):
    """Test data model classes."""

    def test_model_info_creation(self):
        info = ModelInfo(
            id="test-model",
            display_name="Test Model",
            provider="Test",
            provider_key="test",
            category="flagship",
            context_window=128000,
        )
        self.assertEqual(info.display_name, "Test Model")
        self.assertEqual(info.context_window, 128000)

    def test_endpoint_check_result(self):
        result = EndpointCheckResult(
            provider="OpenAI",
            url="https://api.openai.com",
            status="ok",
            latency_ms=150.5,
        )
        self.assertEqual(result.status, "ok")
        self.assertAlmostEqual(result.latency_ms, 150.5)


if __name__ == "__main__":
    unittest.main(verbosity=2)

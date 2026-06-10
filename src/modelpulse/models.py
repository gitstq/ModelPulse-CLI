"""
ModelPulse-CLI - Data Models
Shared data structures and type definitions.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict
from enum import Enum


class ModelCategory(Enum):
    """Model category classification."""
    FLAGSHIP = "flagship"
    COST_EFFECTIVE = "cost_effective"
    REASONING = "reasoning"
    OPEN_SOURCE = "open_source"
    SPECIALIZED = "specialized"


class EndpointStatus(Enum):
    """API endpoint health status."""
    OK = "ok"
    ERROR = "error"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


@dataclass
class BenchmarkScores:
    """Model benchmark scores."""
    mmlu: Optional[float] = None
    human_eval: Optional[float] = None
    math: Optional[float] = None
    swe_bench: Optional[float] = None


@dataclass
class ModelInfo:
    """Complete model information."""
    id: str
    display_name: str
    provider: str
    provider_key: str
    category: str
    context_window: int = 0
    input_price_per_1m: float = 0.0
    output_price_per_1m: float = 0.0
    capabilities: List[str] = field(default_factory=list)
    release_date: str = ""
    benchmark_scores: Dict = field(default_factory=dict)


@dataclass
class EndpointCheckResult:
    """Result of an API endpoint health check."""
    provider: str
    url: str
    status: str
    latency_ms: Optional[float] = None
    http_status: Optional[int] = None
    error: Optional[str] = None
    timestamp: str = ""


@dataclass
class RecommendationResult:
    """Model recommendation result."""
    model_name: str
    provider: str
    score: float
    category: str
    total_cost: float
    capabilities: List[str] = field(default_factory=list)
    score_breakdown: Dict = field(default_factory=dict)


@dataclass
class CostEstimate:
    """Cost estimation for a model usage scenario."""
    model_name: str
    provider: str
    input_tokens: int
    output_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float

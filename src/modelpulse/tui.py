"""
ModelPulse-CLI - TUI Dashboard Module
Rich terminal dashboard for model monitoring and comparison.
Uses only Python stdlib (curses-like rendering with ANSI escape codes).
"""

import os
import sys
import time
from datetime import datetime
from typing import Optional


# ─── ANSI Color Codes ─────────────────────────────────────────────────────────

class Colors:
    """ANSI color code helpers."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"

    # Foreground
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    GRAY = "\033[90m"

    # Background
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    @staticmethod
    def disable():
        """Disable colors (for non-TTY environments)."""
        for attr in ["RESET", "BOLD", "DIM", "UNDERLINE",
                      "BLACK", "RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "WHITE", "GRAY",
                      "BG_BLACK", "BG_RED", "BG_GREEN", "BG_YELLOW", "BG_BLUE", "BG_MAGENTA", "BG_CYAN", "BG_WHITE"]:
            setattr(Colors, attr, "")


def is_tty():
    """Check if stdout is a TTY."""
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def auto_colors():
    """Auto-detect and configure color support."""
    if not is_tty() or os.environ.get("NO_COLOR"):
        Colors.disable()


# ─── Progress Bar ─────────────────────────────────────────────────────────────

def progress_bar(value: float, max_val: float = 100, width: int = 20,
                 filled_char: str = "█", empty_char: str = "░",
                 color: str = None) -> str:
    """Render a progress bar string."""
    ratio = min(1.0, max(0.0, value / max_val)) if max_val > 0 else 0
    filled = int(ratio * width)
    empty = width - filled
    bar = filled_char * filled + empty_char * empty

    if color and is_tty():
        bar = f"{color}{bar}{Colors.RESET}"

    return f"[{bar}] {value:.1f}/{max_val:.0f}"


def score_bar(score: float, width: int = 15) -> str:
    """Render a colored score bar (0-100)."""
    if score >= 80:
        color = Colors.GREEN
    elif score >= 60:
        color = Colors.YELLOW
    elif score >= 40:
        color = Colors.MAGENTA
    else:
        color = Colors.RED
    return progress_bar(score, 100, width, color=color)


# ─── Table Rendering ──────────────────────────────────────────────────────────

def render_table(headers: list, rows: list, col_widths: list = None,
                 header_color: str = None, highlight_fn=None) -> str:
    """
    Render a formatted table.
    highlight_fn: callable(row) -> bool to highlight specific rows.
    """
    if not col_widths:
        col_widths = [max(len(str(h)), max((len(str(r[i])) for r in rows), default=0)) + 2
                      for i, h in enumerate(headers)]

    lines = []

    # Header
    header_line = ""
    for i, h in enumerate(headers):
        w = col_widths[i] if i < len(col_widths) else len(str(h)) + 2
        header_line += f"{str(h):<{w}}"
    if header_color and is_tty():
        header_line = f"{header_color}{Colors.BOLD}{header_line}{Colors.RESET}"
    lines.append(header_line)

    # Separator
    sep = "".join("-" * w for w in col_widths)
    lines.append(sep)

    # Rows
    for row in rows:
        row_line = ""
        for i, cell in enumerate(row):
            w = col_widths[i] if i < len(col_widths) else len(str(cell)) + 2
            row_line += f"{str(cell):<{w}}"
        if highlight_fn and highlight_fn(row) and is_tty():
            row_line = f"{Colors.BG_BLUE}{Colors.WHITE}{row_line}{Colors.RESET}"
        lines.append(row_line)

    return "\n".join(lines)


# ─── Dashboard Components ─────────────────────────────────────────────────────

def render_header(title: str, subtitle: str = "") -> str:
    """Render dashboard header."""
    width = 80
    lines = [
        f"{Colors.CYAN}{Colors.BOLD}{'=' * width}{Colors.RESET}",
        f"{Colors.CYAN}{Colors.BOLD}  {title}{Colors.RESET}",
    ]
    if subtitle:
        lines.append(f"{Colors.DIM}  {subtitle}{Colors.RESET}")
    lines.append(f"{Colors.CYAN}{Colors.BOLD}{'=' * width}{Colors.RESET}")
    return "\n".join(lines)


def render_status_badge(status: str) -> str:
    """Render a colored status badge."""
    badges = {
        "ok": f"{Colors.BG_GREEN}{Colors.WHITE}  OK  {Colors.RESET}",
        "error": f"{Colors.BG_RED}{Colors.WHITE} FAIL {Colors.RESET}",
        "warn": f"{Colors.BG_YELLOW}{Colors.BLACK} WARN {Colors.RESET}",
        "unknown": f"{Colors.BG_BLACK}{Colors.WHITE}  ??  {Colors.RESET}",
    }
    return badges.get(status.lower(), badges["unknown"])


def render_model_card(model: dict, rank: int = 0, score: float = None) -> str:
    """Render a model information card."""
    lines = []
    bm = model.get("benchmark_scores", {})
    total_cost = model.get("input_price_per_1m", 0) + model.get("output_price_per_1m", 0)

    # Title line
    rank_str = f"#{rank} " if rank else ""
    title_color = Colors.GREEN if rank == 1 else (Colors.YELLOW if rank == 2 else (Colors.MAGENTA if rank == 3 else Colors.WHITE))
    lines.append(f"  {title_color}{Colors.BOLD}{rank_str}{model['display_name']}{Colors.RESET} {Colors.DIM}({model['provider']}){Colors.RESET}")

    # Score bar
    if score is not None:
        lines.append(f"  {score_bar(score)}")

    # Info line
    cat = model.get("category", "").replace("_", "-").title()
    info = f"  {Colors.DIM}Category: {cat}  |  Context: {_fmt_ctx(model.get('context_window', 0))}  |  Cost: {_fmt_cost(total_cost)}{Colors.RESET}"
    lines.append(info)

    # Benchmarks
    bench_parts = []
    for name, key in [("MMLU", "mmlu"), ("HumanEval", "human_eval"), ("Math", "math"), ("SWE", "swe_bench")]:
        val = bm.get(key)
        if val:
            color = Colors.GREEN if val >= 85 else (Colors.YELLOW if val >= 70 else Colors.RED)
            bench_parts.append(f"{name}:{color}{val:.1f}{Colors.RESET}")
    if bench_parts:
        lines.append(f"  {'  '.join(bench_parts)}")

    return "\n".join(lines)


def render_monitor_dashboard(results: list) -> str:
    """Render monitoring results dashboard."""
    lines = [render_header("ModelPulse Monitor", f"Real-time API Endpoint Status  |  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")]

    for r in results:
        badge = render_status_badge(r.get("status", "unknown"))
        provider = r.get("provider", "Unknown")
        latency = f"{r.get('latency_ms', 0):.0f}ms" if r.get("latency_ms") else "N/A"
        error = r.get("error", "")

        line = f"  {badge}  {provider:<20} {latency:>8}"
        if error:
            line += f"  {Colors.RED}{error[:40]}{Colors.RESET}"
        lines.append(line)

    # Summary
    ok = sum(1 for r in results if r.get("status") == "ok")
    total = len(results)
    pct = (ok / total * 100) if total > 0 else 0
    color = Colors.GREEN if pct >= 80 else (Colors.YELLOW if pct >= 50 else Colors.RED)
    lines.append(f"\n  {color}{Colors.BOLD}Summary: {ok}/{total} endpoints reachable ({pct:.0f}%){Colors.RESET}")

    return "\n".join(lines)


def render_recommendation_dashboard(recommendations: list, task_name: str) -> str:
    """Render recommendation results dashboard."""
    lines = [render_header("ModelPulse Recommendation", f"Task: {task_name}  |  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")]

    for i, (model, score) in enumerate(recommendations, 1):
        lines.append("")
        lines.append(render_model_card(model, rank=i, score=score))

    return "\n".join(lines)


def render_pricing_dashboard(models: list) -> str:
    """Render pricing comparison dashboard."""
    lines = [render_header("ModelPulse Pricing", f"AI Model Cost Comparison  |  {datetime.now().strftime('%Y-%m-%d')}")]

    headers = ["Model", "Provider", "In $/1M", "Out $/1M", "Total $/1M", "Context"]
    rows = []
    for m in models:
        in_p = m.get("input_price_per_1m", 0)
        out_p = m.get("output_price_per_1m", 0)
        rows.append([
            m["display_name"],
            m["provider"],
            _fmt_cost(in_p),
            _fmt_cost(out_p),
            _fmt_cost(in_p + out_p),
            _fmt_ctx(m.get("context_window", 0)),
        ])

    lines.append(render_table(headers, rows))
    return "\n".join(lines)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _fmt_cost(price: float) -> str:
    if price == 0:
        return "Free"
    return f"${price:.2f}"


def _fmt_ctx(tokens: int) -> str:
    if tokens >= 1_000_000:
        return f"{tokens / 1_000_000:.1f}M"
    if tokens >= 1_000:
        return f"{tokens / 1_000:.0f}K"
    return str(tokens)


def clear_screen():
    """Clear terminal screen."""
    if is_tty():
        print("\033[2J\033[H", end="", flush=True)


def print_banner():
    """Print application banner."""
    auto_colors()
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
   ╔══════════════════════════════════════════════════════════════╗
   ║                                                              ║
   ║   ██████╗ ██████╗ ██████╗ ███████╗   ██████╗ ██████╗ ███████╗║
   ║  ██╔════╝██╔═══██╗██╔══██╗██╔════╝   ██╔══██╗██╔══██╗██╔════╝║
   ║  ██║     ██║   ██║██████╔╝█████╗     ██████╔╝██████╔╝███████╗║
   ║  ██║     ██║   ██║██╔══██╗██╔══╝     ██╔═══╝ ██╔═══╝ ██╔══╝║
   ║  ╚██████╗╚██████╔╝██║  ██║███████╗   ██║     ██║     ███████╗║
   ║   ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝   ╚═╝     ╚═╝     ╚══════╝║
   ║                                                              ║
   ║   AI Model Real-time Monitoring & Intelligent Recommendation ║
   ║   v{VERSION:<54}║
   ║                                                              ║
   ╚══════════════════════════════════════════════════════════════╝{Colors.RESET}
"""
    print(banner)

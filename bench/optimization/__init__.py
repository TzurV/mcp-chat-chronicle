"""Optional, development-only prompt optimization bridge.

This package deliberately imports no optimization framework at module import time.
DSPy and GEPA are loaded only by the compatibility and execution entry points.
"""

from .models import OptimizationConfig, load_optimization_config

__all__ = ["OptimizationConfig", "load_optimization_config"]

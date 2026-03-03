"""Routes initialization."""

# Use package-relative imports so the module can be imported both as
# top-level `routes` (when backend is on PYTHONPATH) and as
# `backend.routes` (when running tests from project root).
from .data import bp as data_bp
from .calculations import bp as calculations_bp
from .analysis import bp as analysis_bp

__all__ = ['data_bp', 'calculations_bp', 'analysis_bp']

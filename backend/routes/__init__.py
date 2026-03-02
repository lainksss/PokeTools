"""Routes initialization."""

from routes.data import bp as data_bp
from routes.calculations import bp as calculations_bp
from routes.analysis import bp as analysis_bp

__all__ = ['data_bp', 'calculations_bp', 'analysis_bp']

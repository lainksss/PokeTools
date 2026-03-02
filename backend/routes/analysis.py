"""Analysis endpoints aggregator.

This module aggregates threat and coverage analysis endpoints.
"""

from flask import Blueprint

from routes.threats import bp as threats_bp
from routes.coverage import bp as coverage_bp

bp = Blueprint('analysis', __name__, url_prefix='/api')

# Register sub-blueprints
bp.register_blueprint(threats_bp)
bp.register_blueprint(coverage_bp)

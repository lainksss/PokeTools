"""Refactored Flask API - Clean Architecture.

This clean architecture splits responsibilities:
- routes/: Endpoint definitions (data, calculations, analysis)
- utils/: Shared utilities (data_loader, helpers)
- api.py: Flask app configuration and blueprint registration
"""

from pathlib import Path
import sys
from flask import Flask
from flask_cors import CORS

# Path setup: ensure backend package can be imported
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

# Create Flask app
app = Flask(__name__)

# Configure CORS
CORS(app, origins=[
    "https://lainksss.github.io",
    "https://lainksss.github.io/PokeTools",
    "http://localhost:5173"
])

# Register blueprints
from routes import data_bp, calculations_bp, analysis_bp

app.register_blueprint(data_bp)
app.register_blueprint(calculations_bp)
app.register_blueprint(analysis_bp)


if __name__ == "__main__":
    import os
    host = os.environ.get("API_HOST", "0.0.0.0")
    port = int(os.environ.get("API_PORT", "5000"))
    app.run(host=host, port=port, debug=True)

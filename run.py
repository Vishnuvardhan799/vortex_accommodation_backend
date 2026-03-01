"""
Quick start script for the Vortex 2026 Accommodation System backend.

Usage:
    python run.py              # Run in development mode with auto-reload
    python run.py --prod       # Run in production mode
"""

import sys
import os
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    # Get the directory where this script is located
    backend_dir = Path(__file__).parent
    env_file = backend_dir / ".env"

    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Loaded environment variables from: {env_file}")
    else:
        print(f"⚠️  Warning: .env file not found at {env_file}")
        print("   Make sure to set environment variables manually or create .env file")
except ImportError:
    print("⚠️  Warning: python-dotenv not installed")
    print("   Install it with: pip install python-dotenv")
    print("   Or set environment variables manually")

import uvicorn

if __name__ == "__main__":
    # Check if production mode is requested
    is_production = "--prod" in sys.argv or "--production" in sys.argv

    if is_production:
        print("Starting server in PRODUCTION mode...")
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            workers=4,
            log_level="info"
        )
    else:
        print("Starting server in DEVELOPMENT mode with auto-reload...")
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="debug"
        )

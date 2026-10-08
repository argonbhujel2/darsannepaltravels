#!/usr/bin/env python
"""Darshan Nepal Travel & Tours — entry point."""
import os
import sys

# Ensure project root is on sys.path (fixes ModuleNotFoundError on some Windows installs)
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

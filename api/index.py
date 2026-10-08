"""Vercel serverless entrypoint."""
import os
import sys

# Mark serverless early so config picks /tmp paths
os.environ.setdefault('VERCEL', '1')
if not os.environ.get('FLASK_ENV'):
    os.environ['FLASK_ENV'] = 'production'

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import create_app

app = create_app()

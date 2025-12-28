"""
Vercel entrypoint - imports the Flask application
"""
from app_supabase import app

# Vercel expects 'app' or 'application'
application = app

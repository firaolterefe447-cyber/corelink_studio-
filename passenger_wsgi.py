import os
import sys
from pathlib import Path

# ==============================================
# PROJECT PATH CONFIGURATION
# ==============================================
PROJECT_DIR = '/home/corelink/corelink_studio-'

# Ensure project directory is in Python path
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# ==============================================
# ENVIRONMENT VARIABLE SETUP
# ==============================================
# Load environment variables from .env file if it exists
env_file = Path(PROJECT_DIR) / '.env'
if env_file.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(env_file)
    except ImportError:
        # python-dotenv not available, continue with hardcoded values
        pass
    except Exception as e:
        # Log error but continue with defaults
        sys.stderr.write(f"Warning: Failed to load .env file: {e}\n")

# ==============================================
# PRODUCTION CONFIGURATION
# ==============================================
# Set critical environment variables with fallbacks
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ.setdefault('ENVIRONMENT', 'production')
os.environ.setdefault('DEBUG', 'False')

# ==============================================
# DATABASE CONFIGURATION VALIDATION
# ==============================================
# Ensure database settings are properly configured
required_db_settings = {
    'DB_ENGINE': 'django.db.backends.postgresql',
    'DB_NAME': 'corelink_studio_db',
    'DB_USER': 'corelink_studioadmin',
    'DB_PASSWORD': 'studioadmin7744$$@@*',
    'DB_HOST': 'localhost',
    'DB_PORT': '5432'
}

for key, default_value in required_db_settings.items():
    os.environ.setdefault(key, default_value)

# ==============================================
# IMPORT DJANGO APPLICATION
# ==============================================
try:
    from config.wsgi import application
except ImportError as e:
    sys.stderr.write(f"Error: Failed to import Django application: {e}\n")
    sys.stderr.write(f"Python path: {sys.path}\n")
    sys.stderr.write(f"Project directory: {PROJECT_DIR}\n")
    raise

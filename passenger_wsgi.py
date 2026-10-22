import os
import sys
from pathlib import Path

PROJECT_DIR = '/home/corelink/corelink_studio-'

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# Load environment variables from .env file if it exists
env_file = Path(PROJECT_DIR) / '.env'
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)

# Set production environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ.setdefault('ENVIRONMENT', 'production')
os.environ.setdefault('DEBUG', 'False')
os.environ.setdefault('DB_ENGINE', 'django.db.backends.postgresql')
os.environ.setdefault('DB_NAME', 'corelink_studio_db')
os.environ.setdefault('DB_USER', 'corelink_studioadmin')
os.environ.setdefault('DB_PASSWORD', 'studioadmin7744$$@@*')
os.environ.setdefault('DB_HOST', 'localhost')
os.environ.setdefault('DB_PORT', '5432')

from config.wsgi import application

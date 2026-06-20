from .base import *
import dj_database_url

DEBUG = False

# Read ALLOWED_HOSTS from env (comma separated)
allowed_hosts_env = os.getenv('ALLOWED_HOSTS', '')
if allowed_hosts_env:
    ALLOWED_HOSTS = allowed_hosts_env.split(',')

# Update DATABASE_URL with dj-database-url
db_from_env = dj_database_url.config(conn_max_age=500)
if db_from_env:
    DATABASES['default'].update(db_from_env)

# Cloudinary configuration
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = False
cors_origins_env = os.getenv('CORS_ALLOWED_ORIGINS', '')
if cors_origins_env:
    CORS_ALLOWED_ORIGINS = cors_origins_env.split(',')

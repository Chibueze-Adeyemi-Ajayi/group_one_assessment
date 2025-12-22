import os
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

db_url = env.db_url('DATABASE_URL', default=f'sqlite:///{BASE_DIR / "db.sqlite3"}')
print(f"DATABASE_URL is missing, defaulting to: {db_url}")

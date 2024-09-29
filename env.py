from decouple import config as decouple_config, Config, RepositoryEnv

from pathlib import Path
from functools import lru_cache

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BASE_DIR.parent
ENV_FILE_PATH = PROJECT_DIR / ".env"

@lru_cache
def get_config():
    if ENV_FILE_PATH.exists():
        return Config(RepositoryEnv(str(ENV_FILE_PATH)))
    return None

# Cargar la configuración
config = get_config() or decouple_config

# Obtener las claves de configuración
SECRET_KEY = config("DJANGO_SECRET_KEY", default=None)
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY", default=None)

# Asignar la clave de Stripe
import stripe
stripe.api_key = STRIPE_SECRET_KEY



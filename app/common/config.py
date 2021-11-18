from dataclasses import dataclass
from os import environ, path

from pydantic import BaseModel

base_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))


@dataclass
class Config:
    """
    Basic Configuration
    """
    BASE_DIR = base_dir
    DB_POOL_RECYCLE: int = 900
    DB_ECHO: bool = True


@dataclass
class LocalConfig(Config):
    DB_URL: str = "mysql+pymysql://root:kbj2277!@localhost/login-chat?charset=utf8mb4"
    PROJ_RELOAD: bool = True
    TRUSTED_HOSTS = ["*"]
    ALLOW_SITE = ["http://localhost:3000"]


@dataclass
class ProdConfig(Config):
    PROJ_RELOAD: bool = False
    TRUSTED_HOSTS = ["*"]
    ALLOW_SITE = ["http://localhost:3000"]


@dataclass
class TestConfig(Config):
    DB_URL: str = "mysql+pymysql://root:kbj2277!@localhost/login-chat-test?charset=utf8mb4"
    TRUSTED_HOSTS = ["*"]
    ALLOW_SITE = ["*"]
    TEST_MODE: bool = True


class JWTConfig(BaseModel):
    authjwt_secret_key: str = "secret"
    # Configure application to store and get JWT from cookies
    authjwt_token_location: set = {"cookies"}
    # Only allow JWT cookies to be sent over https
    authjwt_cookie_secure: bool = False
    # Enable csrf double submit protection. default is True
    authjwt_cookie_csrf_protect: bool = False
    # Change to 'lax' in production to make your website more secure from CSRF Attacks, default is None
    # authjwt_cookie_samesite: str = 'lax'


def conf():
    """
    Load Configuration
    :return:
    """
    config = dict(prod=ProdConfig(), local=LocalConfig(), test=TestConfig())
    return config.get(environ.get("API_ENV", "local"))

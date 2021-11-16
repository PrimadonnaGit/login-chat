from dataclasses import dataclass
from os import environ, path

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
    DB_URL: str = "mysql+pymysql://root:kbj2277!@localhost/login-chat-test?charset=utf8mb4utf8mb4"
    TRUSTED_HOSTS = ["*"]
    ALLOW_SITE = ["*"]
    TEST_MODE: bool = True


def conf():
    """
    Load Configuration
    :return:
    """
    config = dict(prod=ProdConfig(), local=LocalConfig(), test=TestConfig())
    return config.get(environ.get("API_ENV", "local"))

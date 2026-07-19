import os


def _build_db_uri(db_name_env: str, default_name: str) -> str:
    user = os.environ["DB_USER"]
    password = os.environ["DB_PASSWORD"]
    host = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", "3306")
    name = os.environ.get(db_name_env, default_name)
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}?charset=utf8mb4"


class Config:
    SECRET_KEY = os.environ["SECRET_KEY"]
    SQLALCHEMY_DATABASE_URI = _build_db_uri("DB_NAME", "expense_tracker")
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    EXPENSES_PER_PAGE = 20


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = _build_db_uri("TEST_DB_NAME", "expense_tracker_test")
    WTF_CSRF_ENABLED = False

from pydantic import (
    PostgresDsn,
    MySQLDsn,
)
from pydantic_core import MultiHostUrl
from typing import Optional
from pathlib import Path


def db_engine(scheme: str = "sqlite", username: str = "", password: str = "", host: str = "", port: int = 5432, path: str = "") -> str:
    match scheme:
        case "sqlite":
            return f"sqlite:////{Path(__file__).parent.parent.parent.joinpath("pytool.sqlite")}"
        case "postgresql":
            return MultiHostUrl.build(
                scheme="postgresql+psycopg2", 
                username=username, 
                password=password, 
                host=host, 
                port=port, 
                path=path
            ).__str__()
        case "mysql":
            return MultiHostUrl.build(
                scheme="mysql+pymysql", 
                username=username, 
                password=password, 
                host=host, 
                port=port, 
                path=path
            ).__str__()

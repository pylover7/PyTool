from pydantic import (
    AnyUrl,
    BeforeValidator,
    HttpUrl,
    PostgresDsn,
    MySQLDsn,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from typing import Optional


def db_engine(scheme: str, username: str = "", password: str = "", host: str = "", port: int = 5432, path: str = "") -> Optional[PostgresDsn, MySQLDsn]:
      return MultiHostUrl.build(
          scheme="postgresql+psycopg",
          username=self.POSTGRES_USER,
          password=self.POSTGRES_PASSWORD,
          host=self.POSTGRES_SERVER,
          port=self.POSTGRES_PORT,
          path=self.POSTGRES_DB,
      )

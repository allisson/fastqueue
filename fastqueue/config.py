from pydantic import BaseSettings


class Settings(BaseSettings):
    # testing settings
    testing: bool = False

    # log settings
    log_formatter: str = (
        "asctime=%(asctime)s level=%(levelname)s pathname=%(pathname)s line=%(lineno)s message=%(message)s"
    )
    log_level: str = "info"
    log_json_format: bool = True

    # fastapi settings
    debug: bool = False
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    server_reload: bool = False
    server_num_workers: int = 1

    # postgresql settings
    postgresql_host: str
    postgresql_dbname: str
    postgresql_user: str
    postgresql_password: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "fastqueue_"

    def _create_database_url(self, prefix: str) -> str:
        user = self.postgresql_user
        password = self.postgresql_password
        host = self.postgresql_host
        dbname = self.postgresql_dbname
        return f"{prefix}://{user}:{password}@{host}/{dbname}"

    @property
    def database_url(self) -> str:
        return self._create_database_url("postgresql+psycopg2")

    @property
    def async_database_url(self) -> str:
        return self._create_database_url("postgresql+asyncpg")


settings = Settings()

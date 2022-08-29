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
    database_url: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "fastqueue_"


settings = Settings()

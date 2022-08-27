from pydantic import BaseSettings


class Settings(BaseSettings):
    debug: bool = False
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    server_reload: bool = False
    server_num_workers: int = 1
    log_level: str = "info"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "fastqueue_"


settings = Settings()

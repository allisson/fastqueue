from pydantic import BaseSettings


class Settings(BaseSettings):
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
    database_echo: bool = False

    # queue settings
    min_ack_deadline_seconds: int = 1
    max_ack_deadline_seconds: int = 600
    min_message_retention_seconds: int = 600
    max_message_retention_seconds: int = 1209600
    min_message_max_deliveries: int = 1
    max_message_max_deliveries: int = 1000
    queue_cleanup_interval_seconds: int = 60
    min_delivery_delay_seconds: int = 1
    max_delivery_delay_seconds: int = 900

    # prometheus metrics
    enable_prometheus_metrics: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "fastqueue_"


settings = Settings()

from fastqueue.config import Settings


def test_settings():
    expected_url = "postgresql+psycopg2://fastqueue:fastqueue@localhost/fastqueue"
    expected_async_url = "postgresql+asyncpg://fastqueue:fastqueue@localhost/fastqueue"
    settings = Settings()

    assert settings.database_url == expected_url
    assert settings.async_database_url == expected_async_url

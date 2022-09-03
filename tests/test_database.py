from unittest import mock

from fastqueue.database import run_migrations


@mock.patch("fastqueue.database.command")
def test_run_migrations(mock_command):
    run_migrations()

    mock_command.upgrade.assert_called_once_with(mock.ANY, "head")

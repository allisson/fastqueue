import typer

from fastqueue.api import run_server
from fastqueue.database import run_migrations

cli = typer.Typer()


@cli.command("server")
def run_server_command() -> None:
    return run_server()


@cli.command("db-migrate")
def run_migrations_command() -> None:
    return run_migrations()


if __name__ == "__main__":
    cli()

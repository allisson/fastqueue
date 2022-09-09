import typer

from fastqueue.api import run_server
from fastqueue.database import run_migrations
from fastqueue.workers import run_worker

cli = typer.Typer()


@cli.command("server")
def run_server_command() -> None:
    return run_server()


@cli.command("db-migrate")
def run_migrations_command() -> None:
    return run_migrations()


@cli.command("worker")
def run_worker_command() -> None:
    return run_worker()


if __name__ == "__main__":
    cli()

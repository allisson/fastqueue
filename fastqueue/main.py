import uvicorn
from fastapi import FastAPI

from fastqueue.config import settings

app = FastAPI(debug=settings.debug)


@app.get("/")
def read_root():
    return {"Hello": "World"}


def run_server():
    uvicorn.run(
        "fastqueue.main:app",
        debug=settings.debug,
        host=settings.server_host,
        port=settings.server_port,
        log_level=settings.log_level.lower(),
        reload=settings.server_reload,
        workers=settings.server_num_workers,
    )


if __name__ == "__main__":
    run_server()

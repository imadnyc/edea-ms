import uvicorn
from fastapi import FastAPI

from . import db
from .routers import (
    testruns,
    projects,
    specifications,
    measurement_columns,
    measurement_entries,
    forcing_condition,
)

description = """
EDeA MS helps you to consistently store and query data from test runs of your electronics projects.
"""

app = FastAPI(
    title="EDeA Measurement Server",
    description=description,
    version="0.1.0",
    license_info={
        "name": "EUPL 1.2",
        "url": "https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12",
    },
)
app.state.database = db.database
app.include_router(testruns.router)
app.include_router(projects.router)
app.include_router(specifications.router)
app.include_router(measurement_columns.router)
app.include_router(measurement_entries.router)
app.include_router(forcing_condition.router)


@app.on_event("startup")
async def startup() -> None:
    database_ = app.state.database
    if not database_.is_connected:
        await database_.connect()


@app.on_event("shutdown")
async def shutdown() -> None:
    database_ = app.state.database
    if database_.is_connected:
        await database_.disconnect()


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    # to play with API run the script and visit http://127.0.0.1:8000/docs
    uvicorn.run(app, host="127.0.0.1", port=8000)

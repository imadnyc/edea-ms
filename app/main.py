from typing import Any

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

from .routers import (
    testruns,
    projects,
    specifications,
    measurement_columns,
    measurement_entries,
    forcing_condition,
    export,
    jobs,
    config,
)

description = """
EDeA MS helps you to consistently store and query data from test runs of your electronics projects.
"""

tags_metadata = [
    {
        "name": "testrun",
        "description": "Used to batch related measurements (same board, same device) taken typically "
        "without user-interaction. Used to store metadata about the DUT.",
    },
    {
        "name": "specification",
        "description": "Specifications (min, max, typical) of measurement columns",
    },
    {
        "name": "measurement_column",
        "description": "Specify measurement parameters here; set name, description, unit, etc.",
    },
    {
        "name": "measurement_entry",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "forcing_condition",
        "description": "Like *measurement_column* but for forcing conditions (DUT environment / test parameters).",
    },
    {
        "name": "jobqueue",
        "description": "General-purpose distributed task runner FIFO.",
    },
    {
        "name": "projects",
        "description": "Store project names and identifiers.",
    },
    {
        "name": "configuration",
        "description": "Simple key:value store to store application configuration.",
    },
]

app = FastAPI(
    title="EDeA Measurement Server",
    description=description,
    version="0.1.0",
    license_info={
        "name": "EUPL 1.2",
        "url": "https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12",
    },
    openapi_tags=tags_metadata,
)
app.mount("/static", StaticFiles(directory="static"), name="static")
# app.state.database = db.database
app.include_router(testruns.router)
app.include_router(projects.router)
app.include_router(specifications.router)
app.include_router(measurement_columns.router)
app.include_router(measurement_entries.router)
app.include_router(forcing_condition.router)
app.include_router(export.router)
app.include_router(jobs.router)
app.include_router(config.router)


@app.on_event("startup")
async def startup() -> None:
    pass
    # database_ = app.state.database
    # if not database_.is_connected:
    #    await database_.connect()


@app.on_event("shutdown")
async def shutdown() -> None:
    pass
    # database_ = app.state.database
    # if database_.is_connected:
    #    await database_.disconnect()


@app.get("/static/node_modules")
async def forbid() -> Any:
    return Response(status_code=404)


@app.get("/")
async def root() -> Any:
    return RedirectResponse("/static/index.html")

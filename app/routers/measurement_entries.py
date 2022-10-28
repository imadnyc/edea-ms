import json
from typing import List, Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, Response
from ormar import NoMatch
from pydantic import BaseModel

from app.db.models import MeasurementColumn, MeasurementEntry, TestRun

router = APIRouter()


@router.get(
    "/measurement_entries",
    response_model=List[MeasurementEntry],
    tags=["measurement_entry"],
)
async def get_measurement_entries() -> List[MeasurementEntry]:
    items = await MeasurementEntry.objects.all()
    return items


class BatchInput(BaseModel):
    sequence_number: int
    testrun_id: int
    payload: dict[str, Any]


@router.post("/measurement_entries/batch", tags=["measurement_entry"])
async def batch_create_measurement_entries(batch_input: BatchInput) -> Response:
    test_run = await TestRun.objects.get(id=batch_input.testrun_id)
    for k, v in batch_input.payload.items():
        entry = MeasurementEntry(sequence_number=batch_input.sequence_number, testrun=test_run,
                                 column=MeasurementColumn(name=k, project_id=test_run.project.id))
        entry.column = await add_columns_when_needed(entry)
        if type(v) == float or type(v) == int:
            entry.numeric_value = v
        else:
            entry.string_value = str(v)
        await entry.save()
    return Response(status_code=201)


@router.post("/measurement_entries", response_model=MeasurementEntry, tags=["measurement_entry"])
async def create_measurement_entries(entry: MeasurementEntry) -> MeasurementEntry:
    if entry.column is not None:
        if entry.column.id == 0 or entry.column.id is None:
            if entry.column.project_id == 0:
                raise HTTPException(
                    status_code=422,
                    detail={
                        "error": "neither column.id nor project_id are set, can't create new column"
                    },
                )
            entry.column = await add_columns_when_needed(entry)
            # TODO get_or_create() ?
    else:
        raise HTTPException(
            status_code=422, detail={"error": "column information needs to be set"}
        )

    await entry.save()
    return entry


async def add_columns_when_needed(entry: MeasurementEntry) -> MeasurementColumn:
    # create a new column if it does not exist yet
    if entry.column is None:
        raise NotImplementedError("column must be set for measurement_entry")

    try:
        column = await MeasurementColumn.objects.get(
            MeasurementColumn.project_id == entry.column.project_id,
            MeasurementColumn.name == entry.column.name,
        )
        entry.column = column
    except NoMatch:
        await entry.column.save()

    return entry.column


@router.put("/measurement_entries/{id}", tags=["measurement_entry"])
async def get_measurement_entry(id: int, entry: MeasurementEntry) -> MeasurementEntry:
    tx = await MeasurementEntry.objects.get(pk=id)
    return await tx.update(**entry.dict())


@router.delete("/measurement_entries/{id}", tags=["measurement_entry"])
async def delete_measurement_entry(id: int, entry: MeasurementEntry = None) -> JSONResponse:
    if entry:
        return JSONResponse(content={"deleted_rows": await entry.delete()})
    tx = await MeasurementEntry.objects.get(pk=id)
    return JSONResponse(content={"deleted_rows": await tx.delete()})

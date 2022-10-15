from typing import List

from fastapi import APIRouter, HTTPException
from ormar import NoMatch
from pydantic import BaseModel

from app.db.models import MeasurementColumn, MeasurementEntry, TestRun

router = APIRouter()


@router.get(
    "/measurement_entries",
    response_model=List[MeasurementEntry],
    tags=["measurement_entry"],
)
async def get_measurement_entries():
    items = await MeasurementEntry.objects.all()
    return items


class BatchInput(BaseModel):
    sequence_number: int
    testrun_id: int
    payload: dict


@router.post("/measurement_entries/batch", tags=["measurement_entry"])
async def batch_create_measurement_entries(batch_input: BatchInput):
    test_run = await TestRun.objects.get(id=batch_input.testrun_id)
    for k, v in batch_input.payload.items():
        entry = MeasurementEntry(sequence_number=batch_input.sequence_number, testrun=test_run,
                                 column=MeasurementColumn(name=k, project=test_run.project))
        entry.column = await add_columns_when_needed(entry)
        if type(v) == float or type(v) == int:
            entry.numeric_value = v
        else:
            entry.string_value = str(v)
        await entry.save()
    return "Success"


@router.post("/measurement_entries", response_model=MeasurementEntry, tags=["measurement_entry"])
async def create_measurement_entries(entry: MeasurementEntry):
    if entry.column is not None:
        if entry.column.id == 0 or entry.column.id is None:
            if entry.column.project is None or entry.column.project.id is None:
                raise HTTPException(
                    status_code=422,
                    detail={
                        "error": "neither column.id nor project.id are set, can't create new column"
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


async def add_columns_when_needed(entry):
    # create a new column if it does not exist yet
    column = None
    try:
        column = await MeasurementColumn.objects.get(
            MeasurementColumn.project.id == entry.column.project.id,
            MeasurementColumn.name == entry.column.name,
        )
        entry.column = column
    except NoMatch:
        pass
    if column is None:
        await entry.column.save()
    return entry.column


@router.put("/measurement_entries/{id}", tags=["measurement_entry"])
async def get_measurement_entry(id: int, entry: MeasurementEntry):
    tx = await MeasurementEntry.objects.get(pk=id)
    return await tx.update(**entry.dict())


@router.delete("/measurement_entries/{id}", tags=["measurement_entry"])
async def delete_measurement_entry(id: int, entry: MeasurementEntry = None):
    if entry:
        return {"deleted_rows": await entry.delete()}
    tx = await MeasurementEntry.objects.get(pk=id)
    return {"deleted_rows": await tx.delete()}

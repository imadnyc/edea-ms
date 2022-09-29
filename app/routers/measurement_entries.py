from typing import List

from fastapi import APIRouter, HTTPException
from ormar import NoMatch

from app.db.models import MeasurementColumn, MeasurementEntry

router = APIRouter()


@router.get(
    "/measurement_entries/",
    response_model=List[MeasurementEntry],
    tags=["measurement_entry"],
)
async def get_measurement_entries():
    items = await MeasurementEntry.objects.select_related("measurement_entry").all()
    return items


@router.post(
    "/measurement_entries/", response_model=MeasurementEntry, tags=["measurement_entry"]
)
async def create_measurement_entries(entry: MeasurementEntry):
    if entry.column is not None:
        if entry.column.id == 0 or entry.column.id is None:
            # create a new column if it does not exist yet
            column = None

            if entry.column.project is None or entry.column.project.id is None:
                raise HTTPException(
                    status_code=422,
                    detail={
                        "error": "neither column.id nor project.id are set, can't create new column"
                    },
                )
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

        print(entry.column)
    else:
        raise HTTPException(
            status_code=422, detail={"error": "column information needs to be set"}
        )

    await entry.save()
    return entry


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

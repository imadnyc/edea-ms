from typing import List

from fastapi import APIRouter

from app.db.models import MeasurementEntry

router = APIRouter()


@router.get("/measurement_entries/", response_model=List[MeasurementEntry], tags=["measurement_entry"])
async def get_measurement_entries():
    items = await MeasurementEntry.objects.select_related("measurement_entry").all()
    return items


@router.post("/measurement_entries/", response_model=MeasurementEntry, tags=["measurement_entry"])
async def create_measurement_entries(entry: MeasurementEntry):
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

from typing import List

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.db.models import MeasurementColumn

router = APIRouter()


@router.get("/measurement_columns", response_model=List[MeasurementColumn], tags=["measurement_column"])
async def get_measurement_columns() -> List[MeasurementColumn]:
    items = await MeasurementColumn.objects.select_related("project").all()
    return items


@router.post("/measurement_columns", response_model=MeasurementColumn, tags=["measurement_column"])
async def create_measurement_columns(column: MeasurementColumn) -> MeasurementColumn:
    await column.save()
    return column


@router.put("/measurement_columns/{id}", tags=["measurement_column"])
async def get_measurement_column(id: int, column: MeasurementColumn) -> MeasurementColumn:
    tx = await MeasurementColumn.objects.get(pk=id)
    return await tx.update(**column.dict())


@router.delete("/measurement_columns/{id}", tags=["measurement_column"])
async def delete_measurement_column(id: int, column: MeasurementColumn = None) -> JSONResponse:
    if column:
        return JSONResponse(content={"deleted_rows": await column.delete()})
    tx = await MeasurementColumn.objects.get(pk=id)
    return JSONResponse(content={"deleted_rows": await tx.delete()})

from typing import List

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import select

from app.db import models, async_session


class MeasurementColumn(BaseModel):
    class Config:
        orm_mode = True

    id: int | None
    project_id: int
    specification_id: int | None
    name: str
    data_source: str | None
    description: str | None
    user_note: str | None
    measurement_unit: str | None
    flags: int | None


router = APIRouter()


@router.get("/measurement_columns", tags=["measurement_column"])
async def get_measurement_columns() -> List[MeasurementColumn]:
    async with async_session() as session:
        columns: List[MeasurementColumn] = []
        for column in (await session.scalars(select(models.MeasurementColumn))).all():
            columns.append(MeasurementColumn.from_orm(column))

        return columns


@router.post("/measurement_columns", tags=["measurement_column"])
async def create_measurement_column(column: MeasurementColumn) -> MeasurementColumn:
    async with async_session() as session:
        cur = models.MeasurementColumn()
        cur.update_from_model(column)

        session.add(cur)
        await session.commit()

        return MeasurementColumn.from_orm(cur)


@router.put("/measurement_columns/{id}", tags=["measurement_column"])
async def get_measurement_column(id: int) -> MeasurementColumn:
    async with async_session() as session:
        return MeasurementColumn.from_orm(
            (await session.scalars(select(models.MeasurementColumn).where(models.MeasurementColumn.id == id))).one())


@router.delete("/measurement_columns/{id}", tags=["measurement_column"])
async def delete_measurement_column(id: int) -> dict[str, int]:
    async with async_session() as session:
        await session.delete(models.MeasurementColumn(id=id))
        await session.commit()

    return {"deleted_rows": 1}

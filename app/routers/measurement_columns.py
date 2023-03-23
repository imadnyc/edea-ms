from typing import List

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import select

from app.core.auth import CurrentUser
from app.db import async_session, models


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

"""
TODO: whole router subject to removal, not sure if we need this.
      we should evaluate what functionality is needed then in the UI.
"""


@router.get("/measurement_columns", tags=["measurement_column"])
async def get_measurement_columns(
    current_user: CurrentUser,
) -> List[MeasurementColumn]:
    async with async_session() as session:
        columns: List[MeasurementColumn] = [
            MeasurementColumn.from_orm(column)
            for column in (
                await session.scalars(select(models.MeasurementColumn))
            ).all()
        ]
        return columns


@router.post("/measurement_columns", tags=["measurement_column"])
async def create_measurement_column(
    column: MeasurementColumn,
    current_user: CurrentUser,
) -> MeasurementColumn:
    async with async_session() as session:
        cur = models.MeasurementColumn()
        cur.update_from_model(column)

        session.add(cur)
        await session.commit()

        return MeasurementColumn.from_orm(cur)


@router.put("/measurement_columns/{id}", tags=["measurement_column"])
async def get_measurement_column(
    id: int, current_user: CurrentUser
) -> MeasurementColumn:
    async with async_session() as session:
        return MeasurementColumn.from_orm(
            (
                await session.scalars(
                    select(models.MeasurementColumn).where(
                        models.MeasurementColumn.id == id
                    )
                )
            ).one()
        )


@router.delete("/measurement_columns/{id}", tags=["measurement_column"])
async def delete_measurement_column(
    id: int, current_user: CurrentUser
) -> dict[str, int]:
    async with async_session() as session:
        await session.delete(models.MeasurementColumn(id=id))
        await session.commit()

    return {"deleted_rows": 1}

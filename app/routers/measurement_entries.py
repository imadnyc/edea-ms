from datetime import datetime
from typing import List, Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from sqlalchemy import select, and_
from sqlalchemy.exc import NoResultFound

from app.db import models, async_session
from app.db.models import update_from_model
from app.routers.measurement_columns import MeasurementColumn
from app.routers.testruns import TestRun


class MeasurementEntry(BaseModel):
    class Config:
        orm_mode = True

    id: int | None
    sequence_number: int
    numeric_value: float | None
    string_value: str | None
    created_at: datetime | None
    flags: int | None
    column: MeasurementColumn
    testrun_id: int | None


router = APIRouter()


@router.get("/measurement_entries", response_model=List[MeasurementEntry], tags=["measurement_entry"])
async def get_measurement_entries() -> List[MeasurementEntry]:
    async with async_session() as session:
        items: List[MeasurementEntry] = []
        for item in (await session.scalars(select(models.MeasurementEntry))).all():
            items.append(MeasurementEntry.from_orm(item))

        return items


class BatchInput(BaseModel):
    sequence_number: int
    testrun_id: int
    payload: dict[str, Any]  # mapping of column name to result value


@router.post("/measurement_entries/batch", tags=["measurement_entry"])
async def batch_create_measurement_entries(batch_input: BatchInput) -> Response:
    async with async_session() as session:
        measurement_column_ids: dict[str, int]

        test_run = TestRun.from_orm(
            (await session.scalars(select(models.TestRun).where(models.TestRun.id == batch_input.testrun_id))).one())

        for k, v in batch_input.payload.items():
            res = await session.scalars(select(models.MeasurementColumn).where(
                and_(models.MeasurementColumn.name == k, models.MeasurementColumn.project_id == test_run.project_id)))

            try:
                column = res.one()
            except NoResultFound:
                column = None

            if column is None:
                column = models.MeasurementColumn(name=k, project_id=test_run.project_id)
                session.add(column)
                await session.commit()

            entry = models.MeasurementEntry(sequence_number=batch_input.sequence_number, testrun_id=test_run.id,
                                            column_id=column.id)

            if type(v) in [float, int]:
                entry.numeric_value = v
            else:
                entry.string_value = str(v)
            session.add(entry)

        await session.commit()

    return Response(status_code=201)


@router.post("/measurement_entries", response_model=MeasurementEntry, tags=["measurement_entry"])
async def create_measurement_entry(entry: MeasurementEntry) -> MeasurementEntry:
    async with async_session() as session:
        testrun = (await session.scalars(select(models.TestRun).where(models.TestRun.id == entry.testrun_id))).one()

        res = await session.scalars(
            select(models.MeasurementColumn).where(and_(models.MeasurementColumn.name == entry.column.name,
                                                        models.MeasurementColumn.project_id == testrun.project_id)))

        try:
            column = res.one()
        except NoResultFound:
            column = None

        if column is None:
            column = models.MeasurementColumn(name=entry.column.name, project_id=testrun.project_id)
            session.add(column)
            await session.commit()

        new_entry = models.MeasurementEntry(sequence_number=entry.sequence_number, testrun_id=testrun.id,
                                            column_id=column.id)

        if entry.numeric_value is not None:
            new_entry.numeric_value = entry.numeric_value
        else:
            new_entry.string_value = entry.string_value
        session.add(new_entry)

        await session.commit()

    return MeasurementEntry.from_orm(entry)


@router.put("/measurement_entries/{id}", tags=["measurement_entry"])
async def update_measurement_entry(id: int, entry: MeasurementEntry) -> MeasurementEntry:
    async with async_session() as session:
        cur = (await session.scalars(select(models.MeasurementEntry).where(models.MeasurementEntry.id == id))).one()

        e = update_from_model(cur, entry)
        await session.commit()

        return MeasurementEntry.from_orm(e)


@router.delete("/measurement_entries/{id}", tags=["measurement_entry"])
async def delete_measurement_entry(id: int) -> JSONResponse:
    async with async_session() as session:
        await session.delete(models.MeasurementEntry(id=id))
        await session.commit()

    return JSONResponse(content={"deleted_rows": 1})

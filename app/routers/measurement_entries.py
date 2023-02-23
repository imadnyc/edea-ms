from datetime import datetime
from typing import Any, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import and_, select
from sqlalchemy.exc import NoResultFound

from app.db import async_session, models
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


@router.get("/measurement_entries", tags=["measurement_entry"])
async def get_measurement_entries() -> List[MeasurementEntry]:
    async with async_session() as session:
        items: List[MeasurementEntry] = [
            MeasurementEntry.from_orm(item)
            for item in (await session.scalars(select(models.MeasurementEntry))).all()
        ]
        return items


class BatchInput(BaseModel):
    sequence_number: int
    testrun_id: int
    payload: dict[str, Any]  # mapping of column name to result value


@router.post("/measurement_entries/batch", tags=["measurement_entry"], status_code=201)
async def batch_create_measurement_entries(batch_input: BatchInput) -> None:
    async with async_session() as session:
        test_run = TestRun.from_orm(
            (
                await session.scalars(
                    select(models.TestRun).where(
                        models.TestRun.id == batch_input.testrun_id
                    )
                )
            ).one()
        )

        # check first if the run is in the right state
        if test_run.state != models.TestRunState.RUNNING:
            raise HTTPException(
                status_code=400, detail=f"run {test_run.id} is not set to RUNNING state"
            )

        for k, v in batch_input.payload.items():
            res = await session.scalars(
                select(models.MeasurementColumn).where(
                    and_(
                        models.MeasurementColumn.name == k,
                        models.MeasurementColumn.project_id == test_run.project_id,
                    )
                )
            )

            try:
                column = res.one()
            except NoResultFound:
                column = None

            if column is None:
                column = models.MeasurementColumn(
                    name=k, project_id=test_run.project_id
                )
                session.add(column)
                await session.commit()

            entry = models.MeasurementEntry(
                sequence_number=batch_input.sequence_number,
                testrun_id=test_run.id,
                column_id=column.id,
            )

            if type(v) in [float, int]:
                entry.numeric_value = v
            else:
                entry.string_value = str(v)
            session.add(entry)

        await session.commit()


@router.post("/measurement_entries", tags=["measurement_entry"])
async def create_measurement_entry(entry: MeasurementEntry) -> MeasurementEntry:
    async with async_session() as session:
        testrun = (
            await session.scalars(
                select(models.TestRun).where(models.TestRun.id == entry.testrun_id)
            )
        ).one()

        res = await session.scalars(
            select(models.MeasurementColumn).where(
                and_(
                    models.MeasurementColumn.name == entry.column.name,
                    models.MeasurementColumn.project_id == testrun.project_id,
                )
            )
        )

        try:
            column = res.one()
        except NoResultFound:
            column = None

        if column is None:
            column = models.MeasurementColumn(
                name=entry.column.name, project_id=testrun.project_id
            )
            session.add(column)
            await session.commit()

        new_entry = models.MeasurementEntry(
            sequence_number=entry.sequence_number,
            testrun_id=testrun.id,
            column_id=column.id,
        )

        if entry.numeric_value is not None:
            new_entry.numeric_value = entry.numeric_value
        else:
            new_entry.string_value = entry.string_value
        session.add(new_entry)

        await session.commit()

    return MeasurementEntry.from_orm(entry)


@router.put("/measurement_entries/{id}", tags=["measurement_entry"])
async def update_measurement_entry(
    id: int, entry: MeasurementEntry
) -> MeasurementEntry:
    async with async_session() as session:
        cur = (
            await session.scalars(
                select(models.MeasurementEntry).where(models.MeasurementEntry.id == id)
            )
        ).one()

        cur.update_from_model(entry)
        await session.commit()

        return MeasurementEntry.from_orm(cur)


@router.delete("/measurement_entries/{id}", tags=["measurement_entry"])
async def delete_measurement_entry(id: int) -> dict[str, int]:
    async with async_session() as session:
        await session.delete(models.MeasurementEntry(id=id))
        await session.commit()

    return {"deleted_rows": 1}

from typing import List, Any

from fastapi import APIRouter, Response
from pydantic import BaseModel, Json
from sqlalchemy import select, and_
from sqlalchemy.exc import NoResultFound
import polars as pl

from app.db import models, async_session

router = APIRouter()


class TestRun(BaseModel):
    class Config:
        orm_mode = True

    id: int | None
    project_id: int
    short_code: str
    dut_id: str
    machine_hostname: str
    user_name: str
    test_name: str
    data: Json[Any] | None


class TestColumn(BaseModel):
    """
    MeasurementColumn with a few fields omitted
    """

    data_source: str | None
    description: str | None
    user_note: str | None
    measurement_unit: str | None
    flags: int | None


class TestSetup(BaseModel):
    steps: list[dict[str, str | float]]
    columns: dict[str, TestColumn]


@router.get("/testruns", tags=["testrun"])
async def get_all_testruns() -> List[TestRun]:
    async with async_session() as session:
        items: List[TestRun] = [
            TestRun.from_orm(item)
            for item in (await session.scalars(select(models.TestRun))).all()
        ]
        return items


@router.get("/testruns/short_code/{short_code}", tags=["testrun"])
async def get_specific_testrun(short_code: str) -> TestRun:
    async with async_session() as session:
        return TestRun.from_orm(
            (
                await session.scalars(
                    select(models.TestRun).where(
                        models.TestRun.short_code == short_code
                    )
                )
            ).one()
        )


@router.get("/testruns/project/{project_id}", tags=["testrun"])
async def get_project_testruns(project_id: int) -> list[TestRun]:
    async with async_session() as session:
        specs: List[TestRun] = [
            TestRun.from_orm(run)
            for run in (
                (
                    await session.scalars(
                        select(models.TestRun).where(
                            models.TestRun.project_id == project_id
                        )
                    )
                ).all()
            )
        ]
        return specs


@router.post("/testruns", tags=["testrun"])
async def create_testrun(new_run: TestRun) -> TestRun:
    async with async_session() as session:
        res = await session.scalars(
            select(models.TestRun).where(
                models.TestRun.short_code == new_run.short_code
            )
        )
        try:
            run = res.one()
        except NoResultFound:
            run = None

        if run is None:
            run = models.TestRun()
            run.update_from_model(new_run)
            session.add(run)
            await session.commit()

        return TestRun.from_orm(run)


@router.put("/testruns/{run_id}", tags=["testrun"])
async def update_testrun(run_id: int, run: TestRun) -> TestRun:
    async with async_session() as session:
        cur = (
            await session.scalars(
                select(models.TestRun).where(models.TestRun.id == run_id)
            )
        ).one()

        cur.update_from_model(run)
        await session.commit()

        return TestRun.from_orm(cur)


@router.delete("/testruns/{run_id}", tags=["testrun"])
async def delete_testrun(run_id: int) -> dict[str, int]:
    async with async_session() as session:
        await session.delete(models.TestRun(id=run_id))
        await session.commit()

    return {"deleted_rows": 1}


@router.get("/testruns/measurements/{run_id}", tags=["testrun"])
async def testrun_measurements(run_id: int) -> dict:
    async with async_session() as session:
        run = (
            await session.scalars(
                select(models.TestRun).where(models.TestRun.id == run_id)
            )
        ).one()

        cols = await session.scalars(
            select(models.MeasurementColumn).where(
                models.MeasurementColumn.project_id == run.project_id
            )
        )

        entries = (
            await session.scalars(
                select(models.MeasurementEntry).where(
                    models.MeasurementEntry.testrun_id == run_id
                )
            )
        ).all()
        df = pl.DataFrame(entries)
        mcols = df.pivot(index="sequence_number")

        # TODO: combine value columns into one, but how?

        return {"columns": cols, "values": mcols}


@router.post("/testruns/setup/{run_id}", tags=["testrun"])
async def setup_testrun(run_id: int, setup: TestSetup) -> Response:
    async with async_session() as session:
        res = await session.scalars(
            select(models.TestRun).where(models.TestRun.id == run_id)
        )
        try:
            run = res.one()
        except NoResultFound:
            return Response(status_code=404)

        meas_cols: dict[str, models.MeasurementColumn] = {}

        # create the columns first if they don't exist yet
        for name, values in setup.columns.items():
            res = await session.scalars(
                select(models.MeasurementColumn).where(
                    and_(
                        models.MeasurementColumn.name == name,
                        models.MeasurementColumn.project_id == run.project_id,
                    )
                )
            )

            try:
                column = res.one()
            except NoResultFound:
                column = None

            if column is None:
                column = models.MeasurementColumn(
                    name=name,
                    project_id=run.project_id,
                    data_source=values.data_source,
                    description=values.description,
                    user_note=values.user_note,
                    measurement_unit=values.measurement_unit,
                    flags=values.flags,
                )
                session.add(column)

            meas_cols[name] = column

        await session.commit()

    # run a second tx to create the forcing conditions too
    async with async_session() as session:
        for step in setup.steps:
            sequence_number = step["idx"]
            step_names = set(step.keys())
            step_names.discard("idx")
            for name in step_names:
                column = meas_cols[name]
                fc = models.ForcingCondition(
                    column_id=column.id,
                    testrun_id=run.id,
                    sequence_number=sequence_number,
                )
                target_value = step[name]
                if isinstance(target_value, float):
                    fc.numeric_value = target_value
                else:
                    fc.string_value = target_value

                session.add(fc)

        await session.commit()

        return Response(status_code=200)

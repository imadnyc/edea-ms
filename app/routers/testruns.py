import io
from datetime import datetime
from enum import Enum
from typing import Any, List

import polars as pl
from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Json
from sqlalchemy import and_, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.core.auth import CurrentUser
from app.db import async_session, models
from app.db.models import TestRunState

router = APIRouter()


class NewTestRun(BaseModel):
    class Config:
        orm_mode = True

    project_id: int
    short_code: str
    dut_id: str
    machine_hostname: str
    user_name: str
    test_name: str
    data: Json[Any] | None


class TestRun(NewTestRun):
    class Config:
        orm_mode = True

    id: int | None
    created_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    state: TestRunState


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


class DataExportFormat(Enum):
    CSV = "csv"
    JSON = "json"
    PARQUET = "parquet"


@router.get("/testruns", tags=["testrun"])
async def get_all_testruns(
    current_user: CurrentUser,
) -> List[TestRun]:
    async with async_session() as session:
        items: List[TestRun] = [
            TestRun.from_orm(item)
            for item in (
                await session.scalars(
                    select(models.TestRun).where(
                        models.TestRun.user_id == current_user.id
                    )
                )
            ).all()
        ]
        return items


@router.get("/testruns/short_code/{short_code}", tags=["testrun"])
async def get_specific_testrun(short_code: str, current_user: CurrentUser) -> TestRun:
    async with async_session() as session:
        return TestRun.from_orm(
            (
                await session.scalars(
                    select(models.TestRun).where(
                        and_(
                            models.TestRun.short_code == short_code,
                            models.TestRun.user_id == current_user.id,
                        )
                    )
                )
            ).one()
        )


@router.get("/testruns/project/{project_id}", tags=["testrun"])
async def get_project_testruns(
    project_id: int, current_user: CurrentUser
) -> list[TestRun]:
    async with async_session() as session:
        specs: List[TestRun] = [
            TestRun.from_orm(run)
            for run in (
                (
                    await session.scalars(
                        select(models.TestRun).where(
                            and_(
                                models.TestRun.project_id == project_id,
                                models.TestRun.user_id == current_user.id,
                            )
                        )
                    )
                ).all()
            )
        ]
        return specs


@router.post("/testruns", tags=["testrun"], status_code=201)
async def create_testrun(new_run: NewTestRun, current_user: CurrentUser) -> TestRun:
    async with async_session() as session:
        res = await session.scalars(
            select(models.TestRun).where(
                and_(
                    models.TestRun.short_code == new_run.short_code,
                    models.TestRun.user_id == current_user.id,
                )
            )
        )
        try:
            run = res.one()
        except NoResultFound:
            run = None

        if run is None:
            run = models.TestRun(user_id=current_user.id)
            run.update_from_model(new_run)
            session.add(run)
            await session.commit()

        return TestRun.from_orm(run)


@router.put("/testruns/{run_id}", tags=["testrun"])
async def update_testrun(
    run_id: int,
    run: TestRun,
    current_user: CurrentUser,
) -> TestRun:
    async with async_session() as session:
        cur = (
            await session.scalars(
                select(models.TestRun).where(
                    and_(
                        models.TestRun.id == run_id,
                        models.TestRun.user_id == current_user.id,
                    )
                )
            )
        ).one()

        cur.update_from_model(run)
        await session.commit()

        return TestRun.from_orm(cur)


@router.delete("/testruns/{run_id}", tags=["testrun"])
async def delete_testrun(run_id: int, current_user: CurrentUser) -> dict[str, int]:
    async with async_session() as session:
        cur = (
            await session.scalars(
                select(models.TestRun).where(
                    and_(
                        models.TestRun.id == run_id,
                        models.TestRun.user_id == current_user.id,
                    )
                )
            )
        ).one()
        await session.delete(cur)
        await session.commit()

    return {"deleted_rows": 1}


@router.get("/testruns/measurements/{run_id}", tags=["testrun"])
async def testrun_measurements(
    run_id: int,
    current_user: CurrentUser,
    data_format: DataExportFormat
    | None = Query(default=DataExportFormat.JSON, alias="format"),
) -> StreamingResponse:
    """
    This returns the results for a specific measurement run. It first retrieves the conditions, pivots them and then
    merges them together with the results. As a last step, all columns only consisting of null values get removed.
    """
    async with async_session() as session:
        # check if the run exists before we do other more expensive tasks
        run = (
            await session.scalars(
                select(models.TestRun).where(
                    and_(
                        models.TestRun.id == run_id,
                        models.TestRun.user_id == current_user.id,
                    )
                )
            )
        ).one()

        # aliases allow for more compact queries
        me = aliased(models.MeasurementEntry)
        mc = aliased(models.MeasurementColumn)
        fc = aliased(models.ForcingCondition)
        sp = aliased(models.Specification)

        query_conditions = (
            select(
                fc.sequence_number,
                mc.measurement_unit.label("unit"),
                mc.name,
                fc.numeric_value,
                fc.string_value,
            )
            .join(mc, mc.id == fc.column_id)
            .where(fc.testrun_id == run.id)
        )

        conditions = [list(e) for e in await session.execute(query_conditions)]
        schema_cond = {
            c.name: c.type.python_type for c in query_conditions.selected_columns
        }
        cond_df = pl.DataFrame(conditions, schema=schema_cond).pivot(
            values=["string_value", "numeric_value"],
            index="sequence_number",
            columns=["name", "unit"],
        )

        query_measured_entries = (
            select(
                me.numeric_value.label("me_numeric_value"),
                me.string_value.label("me_string_value"),
                sp.name.label("sp_name"),
                sp.minimum.label("sp_min"),
                sp.typical.label("sp_typ"),
                sp.maximum.label("sp_max"),
            )
            .join(mc, mc.id == me.column_id)
            .join(sp, sp.id == mc.specification_id, isouter=True)
            .where(me.testrun_id == run.id)
        )

        measured_entries = [
            list(e) for e in await session.execute(query_measured_entries)
        ]
        schema_meas = {
            c.name: c.type.python_type for c in query_measured_entries.selected_columns
        }
        meas_df = pl.DataFrame(measured_entries, schema=schema_meas)

        df = pl.concat([cond_df, meas_df], how="horizontal")

        # drop columns which are all nulls
        df = df[[s.name for s in df if s.null_count() != df.height]]

        # strip field types from forcing condition column names, they're always either or
        mapping = {
            col: f'fc{col.removeprefix("string_value").removeprefix("numeric_value")}'
            for col in df.schema.keys()
            if col.startswith("string_value_") or col.startswith("numeric_value_")
        }

        df = df.rename(mapping)

        f = io.BytesIO()

        # polars can directly export a variety of formats which works nicely here
        if data_format == DataExportFormat.JSON:
            df.write_json(f)
            media_type = "application/json"
        elif data_format == DataExportFormat.PARQUET:
            df.write_parquet(f)
            media_type = "application/octet-stream"
        elif data_format == DataExportFormat.CSV:
            df.write_csv(f)
            media_type = "text/csv"

        f.seek(0)

        headers = {}
        if data_format != DataExportFormat.JSON:
            headers[
                "Content-Disposition"
            ] = f'attachment; filename="{run.short_code}_{run.dut_id}.{data_format}"'

        return StreamingResponse(f, headers=headers, media_type=media_type)


@router.post("/testruns/setup/{run_id}", tags=["testrun"])
async def setup_testrun(
    run_id: int,
    setup: TestSetup,
    current_user: CurrentUser,
) -> Response:
    async with async_session() as session:
        run = (
            await session.scalars(
                select(models.TestRun).where(
                    and_(
                        models.TestRun.id == run_id,
                        models.TestRun.user_id == current_user.id,
                    )
                )
            )
        ).one()

        # check if the TestRun is already set up or in progress
        if run.state != TestRunState.NEW:
            raise HTTPException(
                400,
                f"run already in state {run.state}, started at {run.started_at} "
                f"by {run.user_name} on {run.machine_hostname}",
            )

        meas_cols: dict[str, models.MeasurementColumn] = {}

        # create the columns first if they don't exist yet
        for name, values in setup.columns.items():
            m_res = await session.scalars(
                select(models.MeasurementColumn).where(
                    and_(
                        models.MeasurementColumn.name == name,
                        models.MeasurementColumn.project_id == run.project_id,
                    )
                )
            )

            try:
                column = m_res.one()
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

    # finally, set the testrun state to SETUP_COMPLETE to accept measurements now
    async with async_session() as session:
        run = (
            await session.scalars(
                select(models.TestRun).where(models.TestRun.id == run_id)
            )
        ).one()
        run.state = TestRunState.SETUP_COMPLETE
        await session.commit()

    return Response(status_code=200)


async def transition_state(
    session: AsyncSession,
    run_id: int,
    to_state: TestRunState,
    current_user: models.User,
) -> TestRun:
    cur = (
        await session.scalars(
            select(models.TestRun).where(
                and_(
                    models.TestRun.id == run_id,
                    models.TestRun.user_id == current_user.id,
                )
            )
        )
    ).one()

    allowed = []

    if cur.state == TestRunState.SETUP_COMPLETE:
        allowed = [TestRunState.FAILED, TestRunState.INTERRUPTED, TestRunState.RUNNING]
    elif cur.state == TestRunState.RUNNING:
        allowed = [TestRunState.FAILED, TestRunState.INTERRUPTED, TestRunState.COMPLETE]

    if to_state in allowed:
        cur.state = to_state
    else:
        msg = f"testrun {run_id} not in one of the following allowed states: {allowed}"
        raise HTTPException(status_code=400, detail=msg)

    return TestRun.from_orm(cur)


@router.put("/testruns/start/{run_id}", tags=["testrun"])
async def start_testrun(run_id: int, current_user: CurrentUser) -> TestRun:
    async with async_session() as session:
        cur = await transition_state(
            session, run_id, TestRunState.RUNNING, current_user
        )
        cur.completed_at = datetime.now()
        await session.commit()

        return TestRun.from_orm(cur)


@router.put("/testruns/complete/{run_id}", tags=["testrun"])
async def complete_testrun(run_id: int, current_user: CurrentUser) -> TestRun:
    async with async_session() as session:
        cur = await transition_state(
            session, run_id, TestRunState.COMPLETE, current_user
        )
        cur.completed_at = datetime.now()
        await session.commit()

        return TestRun.from_orm(cur)


@router.put("/testruns/fail/{run_id}", tags=["testrun"])
async def fail_testrun(run_id: int, current_user: CurrentUser) -> TestRun:
    async with async_session() as session:
        cur = await transition_state(session, run_id, TestRunState.FAILED, current_user)
        cur.completed_at = datetime.now()
        await session.commit()

        return TestRun.from_orm(cur)

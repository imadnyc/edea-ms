from typing import List, Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Json
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

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


@router.get("/testruns", tags=["testrun"])
async def get_all_testruns() -> List[TestRun]:
    async with async_session() as session:
        items: List[TestRun] = []
        for item in (await session.scalars(select(models.TestRun))).all():
            items.append(TestRun.from_orm(item))

        return items


@router.get("/testruns/short_code/{short_code}", tags=["testrun"])
async def get_specific_testrun(short_code: str) -> TestRun:
    async with async_session() as session:
        return TestRun.from_orm(
            (await session.scalars(select(models.TestRun).where(models.TestRun.short_code == short_code))).one())


@router.post("/testruns", tags=["testrun"])
async def create_testrun(new_run: TestRun) -> TestRun:
    async with async_session() as session:
        res = await session.scalars(select(models.TestRun).where(models.TestRun.short_code == new_run.short_code))
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
        cur = (await session.scalars(select(models.TestRun).where(models.TestRun.id == run_id))).one()

        cur.update_from_model(run)
        await session.commit()

        return TestRun.from_orm(cur)


@router.delete("/testruns/{run_id}", tags=["testrun"])
async def delete_testrun(run_id: int) -> dict[str, int]:
    async with async_session() as session:
        await session.delete(models.TestRun(id=run_id))
        await session.commit()

    return {"deleted_rows": 1}

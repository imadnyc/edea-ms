from typing import List

from fastapi import APIRouter

from app.db.models import TestRun

router = APIRouter()


@router.get("/testruns", response_model=List[TestRun], tags=["testrun"])
async def get_all_testruns():
    items = await TestRun.objects.select_related("project").all()
    return items


@router.get("/testruns/short_code/{short_code}", response_model=List[TestRun], tags=["testrun"])
async def get_specific_testrun(short_code):
    item = await TestRun.objects.select_related("project").get(short_code=short_code)
    return item


@router.post("/testruns", response_model=TestRun, tags=["testrun"])
async def create_testruns(run: TestRun):
    already_exist = await TestRun.objects.filter(short_code=run.short_code).exists()
    if not already_exist:
        await run.save()
    entry = await TestRun.objects.get(short_code=run.short_code)
    return entry


@router.put("/testruns/{run_id}", tags=["testrun"])
async def get_testrun(run_id: int, run: TestRun):
    tx = await TestRun.objects.get(pk=run_id)
    return await tx.update(**run.dict())


@router.delete("/testruns/{run_id}", tags=["testrun"])
async def delete_testrun(run_id: int, run: TestRun = None):
    if run:
        return {"deleted_rows": await run.delete()}
    tx = await TestRun.objects.get(pk=run_id)
    return {"deleted_rows": await tx.delete()}

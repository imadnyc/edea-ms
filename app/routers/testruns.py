from typing import List

from fastapi import APIRouter

from app.db.models import TestRun

router = APIRouter()


@router.get("/testruns/", response_model=List[TestRun], tags=["testrun"])
async def get_testruns():
    items = await TestRun.objects.select_related("project").all()
    return items


@router.post("/testruns/", response_model=TestRun, tags=["testrun"])
async def create_testruns(run: TestRun):
    await run.save()
    return run


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

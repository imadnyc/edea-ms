import datetime
from typing import List

from fastapi import APIRouter, Request
from ormar import NoMatch

from app.db.models import JobQueue, JobState

router = APIRouter()


@router.get("/jobs/all", response_model=List[JobQueue], tags=["jobqueue"])
async def get_all_jobs():
    items = await JobQueue.objects.all()
    return items


@router.get("/jobs/new", response_model=JobQueue, tags=["jobqueue"])
async def get_new_job(request: Request):
    try:
        item = await JobQueue.objects.first(state=JobState.NEW)
        worker = None
        if hasattr(request, "client_host"):
            worker = request.client_host
        await item.update(state=JobState.PENDING, worker=worker, updated_at=datetime.datetime.utcnow())
    except NoMatch:
        item = None
    return item


@router.get("/jobs/{job_id}", response_model=JobQueue, tags=["jobqueue"])
async def get_specific_job(job_id: int):
    item = await JobQueue.objects.get(id=job_id)
    return item


@router.post("/jobs/new", response_model=JobQueue, tags=["jobqueue"])
async def create_job(task: JobQueue):
    task.state = JobState.NEW
    task.updated_at = datetime.datetime.utcnow()
    await task.save()
    return task


@router.put("/jobs/{job_id}", tags=["jobqueue"])
async def update_specific_job(job_id: int, task: JobQueue):
    tx = await JobQueue.objects.get(pk=job_id)
    return await tx.update(**task.dict())


@router.delete("/jobs/{job_id}", tags=["jobqueue"])
async def delete_job(job_id: int, request: Request):
    try:
        item = await JobQueue.objects.get(id=job_id)
        worker = None
        if hasattr(request, "client_host"):
            worker = request.client_host
        await item.update(state=JobState.COMPLETE, worker=worker, updated_at=datetime.datetime.utcnow())
    except NoMatch:
        item = None
    return item

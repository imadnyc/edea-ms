from datetime import datetime, timezone
from typing import List, Any

from fastapi import APIRouter, Request
from pydantic import BaseModel
from sqlalchemy.exc import NoResultFound
from sqlalchemy.sql import select

from app.db import async_session
from app.db import models
from app.db.models import JobState

router = APIRouter()


class Job(BaseModel):
    class Config:
        orm_mode = True

    id: int | None
    state: JobState | None
    worker: str | None
    updated_at: datetime | None
    function_call: str
    parameters: dict[Any, Any]


class NewJob(BaseModel):
    function_call: str
    parameters: dict[Any, Any]


@router.get("/jobs/all", tags=["jobqueue"])
async def get_all_jobs() -> List[Job]:
    async with async_session() as session:
        jobs: List[Job] = [
            Job.from_orm(job)
            for job in (await session.scalars(select(models.Job))).all()
        ]
        return jobs


@router.get("/jobs/new", tags=["jobqueue"])
async def get_new_job(request: Request) -> Job | None:
    async with async_session() as session:
        try:
            res = await session.scalars(
                select(models.Job).where(models.Job.state == JobState.NEW)
            )
            item = res.first()
            if item is None:
                return None

            if request.client is not None:
                item.worker = request.client.host
            item.state = JobState.PENDING
            item.updated_at = datetime.now(timezone.utc)

            await session.commit()
        except NoResultFound:
            item = None

        return Job.from_orm(item)


@router.get("/jobs/{job_id}", tags=["jobqueue"])
async def get_specific_job(job_id: int) -> Job:
    async with async_session() as session:
        return Job.from_orm(
            (
                await session.scalars(select(models.Job).where(models.Job.id == job_id))
            ).one()
        )


@router.post("/jobs/new", tags=["jobqueue"])
async def create_job(new_task: NewJob) -> Job:
    async with async_session() as session:
        task = models.Job(
            state=JobState.NEW,
            updated_at=datetime.now(timezone.utc),
            function_call=new_task.function_call,
            parameters=new_task.parameters,
        )

        session.add(task)
        await session.commit()

        return Job.from_orm(task)


@router.put("/jobs/{job_id}", tags=["jobqueue"])
async def update_specific_job(job_id: int, task: Job) -> Job:
    async with async_session() as session:
        job = (
            await session.scalars(select(models.Job).where(models.Job.id == job_id))
        ).one()

        session.add(job.update_from_model(task))
        await session.commit()

        return Job.from_orm(job)


@router.delete("/jobs/{job_id}", tags=["jobqueue"])
async def delete_job(job_id: int, request: Request) -> Job | None:
    async with async_session() as session:
        try:
            item = (
                await session.scalars(select(models.Job).where(models.Job.id == job_id))
            ).one()
            if item is None:
                return None

            item.state = JobState.COMPLETE
            item.updated_at = datetime.now()
            if request.client is not None:
                item.worker = request.client.host

            session.add(item)
            await session.commit()
        except NoResultFound:
            item = None
        return Job.from_orm(item)

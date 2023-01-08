from typing import List

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import select

from app.db import models, async_session

router = APIRouter()


class Project(BaseModel):
    class Config:
        orm_mode = True

    id: int | None
    number: str
    name: str


@router.get("/projects", tags=["projects"])
async def get_projects() -> List[Project]:
    async with async_session() as session:
        projects: List[Project] = []
        for project in (await session.scalars(select(models.Project))).all():
            projects.append(Project.from_orm(project))

        return projects


@router.post("/projects", tags=["projects"])
async def create_project(project: Project) -> Project:
    async with async_session() as session:
        cur = models.Project()
        cur.update_from_model(project)

        session.add(cur)
        await session.commit()

        return Project.from_orm(cur)


@router.put("/projects/{id}", tags=["projects"])
async def update_project(id: int, project: Project) -> Project:
    async with async_session() as session:
        cur = (await session.scalars(select(models.Project).where(models.Project.id == id))).one()

        cur.update_from_model(project)
        await session.commit()

        return Project.from_orm(cur)


@router.delete("/projects/{id}", tags=["projects"])
async def delete_project(id: int) -> dict[str, int]:
    async with async_session() as session:
        await session.delete(models.Project(id=id))
        await session.commit()

    return {"deleted_rows": 1}

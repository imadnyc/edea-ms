from typing import List

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import select

from app.db import models, async_session
from app.db.models import update_from_model

router = APIRouter()


class Project(BaseModel):
    class Config:
        orm_mode = True

    id: int | None
    number: str
    name: str


@router.get("/projects", response_model=List[Project], tags=["projects"])
async def get_projects() -> List[Project]:
    async with async_session() as session:
        projects: List[Project] = []
        for project in (await session.scalars(select(models.Project))).all():
            projects.append(Project.from_orm(project))

        return projects


@router.post("/projects", response_model=Project, tags=["projects"])
async def create_project(project: Project) -> Project:
    async with async_session() as session:
        cur = update_from_model(models.Project(), project)

        session.add(cur)
        await session.commit()

        return Project.from_orm(cur)


@router.put("/projects/{id}", tags=["projects"])
async def update_project(id: int, project: Project) -> Project:
    async with async_session() as session:
        cur = (await session.scalars(select(models.Project).where(models.Project.id == id))).one()

        update_from_model(cur, project)
        await session.commit()

        return Project.from_orm(cur)


@router.delete("/projects/{id}", tags=["projects"])
async def delete_project(id: int) -> JSONResponse:
    async with async_session() as session:
        await session.delete(models.Project(id=id))
        await session.commit()

    return JSONResponse(content={"deleted_rows": 1})

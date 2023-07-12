from typing import Annotated, List

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import and_, select

from app.core.auth import CurrentUser
from app.core.helpers import prj_unique_field, tryint
from app.db import async_session, models

router = APIRouter()


class Project(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    short_code: str
    name: str


@router.get("/projects", tags=["projects"])
async def get_projects(
    current_user: CurrentUser,
) -> List[Project]:
    async with async_session() as session:
        projects: List[Project] = [
            Project.model_validate(project)
            for project in (
                await session.scalars(
                    select(models.Project).where(
                        models.Project.user_id == current_user.id
                    )
                )
            ).all()
        ]
        return projects


@router.get("/projects/{ident}", tags=["testrun"])
async def get_specific_project(
    ident: Annotated[int | str, Depends(tryint)], current_user: CurrentUser
) -> Project:
    async with async_session() as session:
        return Project.model_validate(
            (
                await session.scalars(
                    select(models.Project).where(
                        and_(
                            prj_unique_field(ident) == ident,
                            models.Project.user_id == current_user.id,
                        )
                    )
                )
            ).one()
        )


@router.post("/projects", tags=["projects"])
async def create_project(project: Project, current_user: CurrentUser) -> Project:
    async with async_session() as session:
        cur = models.Project(user_id=current_user.id)
        cur.update_from_model(project)

        session.add(cur)
        await session.commit()

        return Project.model_validate(cur)


@router.put("/projects/{ident}", tags=["projects"])
async def update_project(
    ident: Annotated[int | str, Depends(tryint)],
    project: Project,
    current_user: CurrentUser,
) -> Project:
    async with async_session() as session:
        cur = (
            await session.scalars(
                select(models.Project).where(
                    and_(
                        prj_unique_field(ident) == ident,
                        models.Project.user_id == current_user.id,
                    )
                )
            )
        ).one()

        cur.update_from_model(project)
        await session.commit()

        return Project.model_validate(cur)


@router.delete("/projects/{ident}", tags=["projects"])
async def delete_project(
    ident: Annotated[int | str, Depends(tryint)], current_user: CurrentUser
) -> dict[str, int]:
    async with async_session() as session:
        cur = (
            await session.scalars(
                select(models.Project).where(
                    and_(
                        prj_unique_field(ident) == ident,
                        models.Project.user_id == current_user.id,
                    )
                )
            )
        ).one()
        await session.delete(cur)
        await session.commit()

    return {"deleted_rows": 1}

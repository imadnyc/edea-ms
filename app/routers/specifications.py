from typing import List, Sequence

import sqlalchemy
from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser
from app.db import async_session, models


class Specification(BaseModel):
    class Config:
        orm_mode = True

    id: int | None
    project_id: int
    name: str
    unit: str
    minimum: float | None
    typical: float | None
    maximum: float | None


router = APIRouter()


async def get_user_project_ids(
    current_user: models.User, session: AsyncSession
) -> Sequence[int]:
    return (
        await session.scalars(
            select(models.Project.id).where(models.Project.user_id == current_user.id)
        )
    ).all()


async def has_user_project_access(
    project_id: int, current_user: models.User, session: AsyncSession
) -> None:
    try:
        (
            await session.scalars(
                select(models.Project).where(
                    and_(
                        models.Project.id == project_id,
                        models.Project.user_id == current_user.id,
                    )
                )
            )
        ).one()
    except sqlalchemy.exc.NoResultFound as e:
        # TODO: handle user access exception
        raise e


@router.get("/specifications", tags=["specification"])
async def get_specifications(
    current_user: CurrentUser,
) -> List[Specification]:
    async with async_session() as session:
        project_ids = await get_user_project_ids(current_user, session)
        specs: List[Specification] = [
            Specification.from_orm(spec)
            for spec in (
                await session.scalars(
                    select(models.Specification).where(
                        models.Specification.project_id.in_(project_ids)
                    )
                )
            ).all()
        ]
        return specs


@router.get("/specifications/project/{project_id}", tags=["specification"])
async def get_project_specifications(
    project_id: int, current_user: CurrentUser
) -> list[Specification]:
    async with async_session() as session:
        # check if project is owned by the user
        await has_user_project_access(project_id, current_user, session)

        specs: List[Specification] = [
            Specification.from_orm(spec)
            for spec in (
                (
                    await session.scalars(
                        select(models.Specification).where(
                            models.Specification.project_id == project_id
                        )
                    )
                ).all()
            )
        ]
        return specs


@router.post("/specifications", tags=["specification"])
async def create_specification(
    spec: Specification, current_user: CurrentUser
) -> Specification:
    async with async_session() as session:
        await has_user_project_access(spec.project_id, current_user, session)

        cur = models.Specification()
        cur.update_from_model(spec)

        session.add(cur)
        await session.commit()

        return Specification.from_orm(cur)


@router.put("/specifications/{id}", tags=["specification"])
async def update_specification(
    id: int,
    spec: Specification,
    current_user: CurrentUser,
) -> Specification:
    async with async_session() as session:
        await has_user_project_access(spec.project_id, current_user, session)

        cur = (
            await session.scalars(
                select(models.Specification).where(models.Specification.id == id)
            )
        ).one()

        cur.update_from_model(spec)
        await session.commit()

        return Specification.from_orm(cur)


@router.delete("/specifications/{id}", tags=["specification"])
async def delete_specification(id: int, current_user: CurrentUser) -> dict[str, int]:
    async with async_session() as session:
        project_ids = await get_user_project_ids(current_user, session)

        spec = (
            await session.scalars(
                select(models.Specification).where(
                    and_(
                        models.Specification.id == id,
                        models.Specification.project_id.in_(project_ids),
                    )
                )
            )
        ).one()

        await session.delete(spec)
        await session.commit()

    return {"deleted_rows": 1}

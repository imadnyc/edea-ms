from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from app.db import models, async_session


class Setting(BaseModel):
    class Config:
        orm_mode = True

    key: str
    value: str


router = APIRouter()


@router.get("/config", tags=["configuration"])
async def get_all_configuration_variables() -> List[Setting]:
    items: List[Setting] = []

    async with async_session() as session:
        for item in (await session.scalars(select(models.Setting))).all():
            items.append(Setting.from_orm(item))

    return items


@router.get("/config/{key}", tags=["configuration"])
async def get_specific_variable(key: str) -> Setting:
    async with async_session() as session:
        return Setting.from_orm((await session.scalars(select(models.Setting).where(models.Setting.key == key))).one())


"""
    if Setting.objects.filter(key=setting.key).exist():
        raise HTTPException(
            status_code=422,
            detail={
                "error": f"Can't add {setting.key!r}; it already exists in the database. (use PUT to update)"
            })
    else:
"""


@router.post("/config", tags=["configuration"])
async def add_variable(setting: Setting) -> Setting:
    async with async_session() as session:
        s = models.Setting(name=setting.key, value=setting.value)

        session.add(s)
        await session.commit()

        return Setting.from_orm(s)


@router.put("/config", tags=["configuration"])
async def update_variable(setting: Setting) -> Setting:
    async with async_session() as session:
        try:
            cur = (await session.scalars(select(models.Setting).where(models.Setting.key == setting.key))).one()

            cur.update_from_model(setting)
            await session.commit()

            return Setting.from_orm(cur)
        except NoResultFound as e:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": f"Can't modify {setting.key!r}; it doesn't exists in the database. (use POST to create)"
                },
            ) from e


@router.delete("/config/{key}", tags=["configuration"])
async def delete_variable(key: str) -> dict[str, int]:
    async with async_session() as session:
        await session.delete(models.Setting(key=key))
        await session.commit()

    return {"deleted_rows": 1}

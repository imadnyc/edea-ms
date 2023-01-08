from typing import List

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import select

from app.db import models, async_session


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


@router.get("/specifications", tags=["specification"])
async def get_specifications() -> List[Specification]:
    async with async_session() as session:
        specs: List[Specification] = []
        for spec in (await session.scalars(select(models.Specification))).all():
            specs.append(Specification.from_orm(spec))

        return specs


@router.post("/specifications", tags=["specification"])
async def create_specification(spec: Specification) -> Specification:
    async with async_session() as session:
        cur = models.Specification()
        cur.update_from_model(spec)

        session.add(cur)
        await session.commit()

        return Specification.from_orm(cur)


@router.put("/specifications/{id}", tags=["specification"])
async def update_specification(id: int, spec: Specification) -> Specification:
    async with async_session() as session:
        cur = (await session.scalars(select(models.Specification).where(models.Specification.id == id))).one()

        cur.update_from_model(spec)
        await session.commit()

        return Specification.from_orm(cur)


@router.delete("/specifications/{id}", tags=["specification"])
async def delete_specification(id: int) -> dict[str, int]:
    async with async_session() as session:
        await session.delete(models.Specification(id=id))
        await session.commit()

    return {"deleted_rows": 1}

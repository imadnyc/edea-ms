from typing import List

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import select

from app.db import models, async_session


class ForcingCondition(BaseModel):
    class Config:
        orm_mode = True

    id: int | None
    column_id: int
    testrun_id: int
    sequence_number: int
    numeric_value: float | None
    string_value: str | None


router = APIRouter()


@router.get("/forcing_conditions", tags=["forcing_condition"])
async def get_forcing_conditions() -> List[ForcingCondition]:
    async with async_session() as session:
        items: List[ForcingCondition] = [
            ForcingCondition.from_orm(item)
            for item in (
                await session.scalars(select(models.ForcingCondition))
            ).all()
        ]
        return items


@router.post("/forcing_conditions", tags=["forcing_condition"])
async def create_forcing_conditions(condition: ForcingCondition) -> ForcingCondition:
    async with async_session() as session:
        cond = models.ForcingCondition()
        session.add(cond.update_from_model(condition))

        await session.commit()

        return ForcingCondition.from_orm(cond)


@router.put("/forcing_conditions/{id}", tags=["forcing_condition"])
async def update_forcing_condition(id: int, condition: ForcingCondition) -> ForcingCondition:
    async with async_session() as session:
        cur = (await session.scalars(select(models.ForcingCondition).where(models.ForcingCondition.id == id))).one()

        cur.update_from_model(condition)
        await session.commit()

        return ForcingCondition.from_orm(cur)


@router.delete("/forcing_conditions/{id}", tags=["forcing_condition"])
async def delete_forcing_condition(id: int) -> dict[str, int]:
    async with async_session() as session:
        await session.delete(models.ForcingCondition(id=id))
        await session.commit()

    return {"deleted_rows": 1}

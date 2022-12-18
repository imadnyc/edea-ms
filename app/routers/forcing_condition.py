from typing import List

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import select

from app.db import models, async_session


class ForcingCondition(BaseModel):
    class Config:
        orm_mode = True

    id: int | None
    measurement_column_id: int
    test_run_id: int
    sequence_number: int
    numeric_value: float | None
    string_value: str | None


router = APIRouter()


@router.get("/forcing_conditions", response_model=List[ForcingCondition], tags=["forcing_condition"])
async def get_forcing_conditions() -> List[ForcingCondition]:
    async with async_session() as session:
        items: List[ForcingCondition] = []
        for item in (await session.scalars(select(models.ForcingCondition))).all():
            items.append(ForcingCondition.from_orm(item))

        return items


@router.post("/forcing_conditions", response_model=ForcingCondition, tags=["forcing_condition"])
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
async def delete_forcing_condition(id: int) -> JSONResponse:
    async with async_session() as session:
        await session.delete(models.ForcingCondition(id=id))
        await session.commit()

    return JSONResponse(content={"deleted_rows": 1})

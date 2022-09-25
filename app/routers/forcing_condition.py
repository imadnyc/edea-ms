from typing import List

from fastapi import APIRouter

from app.db.models import ForcingCondition

router = APIRouter()


@router.get("/forcing_conditions/", response_model=List[ForcingCondition], tags=["forcing_condition"])
async def get_forcing_conditions():
    items = await ForcingCondition.objects.select_related("forcing_condition").all()
    return items


@router.post("/forcing_conditions/", response_model=ForcingCondition, tags=["forcing_condition"])
async def create_forcing_conditions(condition: ForcingCondition):
    await condition.save()
    return condition


@router.put("/forcing_conditions/{id}", tags=["forcing_condition"])
async def get_forcing_condition(id: int, condition: ForcingCondition):
    tx = await ForcingCondition.objects.get(pk=id)
    return await tx.update(**condition.dict())


@router.delete("/forcing_conditions/{id}", tags=["forcing_condition"])
async def delete_forcing_condition(id: int, condition: ForcingCondition = None):
    if condition:
        return {"deleted_rows": await condition.delete()}
    tx = await ForcingCondition.objects.get(pk=id)
    return {"deleted_rows": await tx.delete()}

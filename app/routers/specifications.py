from typing import List

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.db.models import Specification

router = APIRouter()


@router.get("/specifications", response_model=List[Specification], tags=["specification"])
async def get_specifications() -> List[Specification]:
    items = await Specification.objects.select_related("specification").all()
    return items


@router.post("/specifications", response_model=Specification, tags=["specification"])
async def create_specifications(spec: Specification) -> Specification:
    await spec.save()
    return spec


@router.put("/specifications/{id}", tags=["specification"])
async def get_specification(id: int, spec: Specification) -> Specification:
    tx = await Specification.objects.get(pk=id)
    return await tx.update(**spec.dict())


@router.delete("/specifications/{id}", tags=["specification"])
async def delete_specification(id: int, spec: Specification = None) -> JSONResponse:
    if spec:
        return JSONResponse(content={"deleted_rows": await spec.delete()})
    tx = await Specification.objects.get(pk=id)
    return JSONResponse(content={"deleted_rows": await tx.delete()})

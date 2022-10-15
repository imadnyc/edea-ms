from typing import List

from fastapi import APIRouter, HTTPException

from app.db.models import Setting

router = APIRouter()


@router.get("/config", response_model=List[Setting], tags=["configuration"])
async def get_all_configuration_variables():
    entries = await Setting.objects.all()
    return entries


@router.get("/config/{key}", response_model=Setting, tags=["configuration"])
async def get_specific_variable(key: str):
    entry = await Setting.objects.get(key=key)
    return entry


"""
    if Setting.objects.filter(key=setting.key).exist():
        raise HTTPException(
            status_code=422,
            detail={
                "error": f"Can't add {setting.key!r}; it already exists in the database. (use PUT to update)"
            })
    else:
"""


@router.post("/config", response_model=Setting, tags=["configuration"])
async def add_variable(setting: Setting):
    entry = await setting.save()
    return entry


@router.put("/config", response_model=Setting, tags=["configuration"])
async def update_variable(setting: Setting):
    if not Setting.objects.filter(key=setting.key).exist():
        raise HTTPException(
            status_code=422,
            detail={
                "error": f"Can't modify {setting.key!r}; it doesn't exists in the database. (use POST to create)"
            })
    else:
        entry = await Setting.objects.get(key=setting.key)
        entry.value = setting.value
        entry.save()
    return entry


@router.delete("/config/{key}", tags=["configuration"])
async def delete_variable(key: str):
    entry = await Setting.objects.get(key=key)
    entry.delete()
    return

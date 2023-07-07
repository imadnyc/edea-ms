from app.db import models


async def tryint(ident: str) -> int | str:
    try:
        return int(ident)
    except ValueError:
        return ident


def tr_unique_field(id):
    return models.TestRun.short_code if isinstance(id, str) else models.TestRun.id


def prj_unique_field(id: int | str):
    return models.Project.number if isinstance(id, str) else models.Project.id

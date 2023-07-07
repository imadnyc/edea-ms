from app.db import models
from sqlalchemy.orm import InstrumentedAttribute


async def tryint(ident: str) -> int | str:
    try:
        return int(ident)
    except ValueError:
        return ident


def tr_unique_field(
    id: int | str,
) -> InstrumentedAttribute[int] | InstrumentedAttribute[str]:
    return models.TestRun.short_code if isinstance(id, str) else models.TestRun.id


def prj_unique_field(
    id: int | str,
) -> InstrumentedAttribute[int] | InstrumentedAttribute[str]:
    return models.Project.number if isinstance(id, str) else models.Project.id

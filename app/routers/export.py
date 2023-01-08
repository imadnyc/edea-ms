from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import aiosqlite
from fastapi import APIRouter
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from ..db import DATABASE_URL

router = APIRouter()


@router.get("/export/db", response_class=FileResponse)
async def export_database() -> Any:
    dbfile = DATABASE_URL.replace('sqlite:///', '')
    main_db = await aiosqlite.connect(dbfile)
    db_name = Path(dbfile).name
    backup_dir = TemporaryDirectory()
    backup_path = Path(backup_dir.name, db_name)
    backup_db = await aiosqlite.connect(backup_path)

    await main_db.backup(backup_db)

    await backup_db.close()
    await main_db.close()

    # return the database backup and remove it afterwards
    return FileResponse(
        path=backup_path,
        media_type='application/vnd.sqlite3',
        filename=db_name,
        background=BackgroundTask(backup_dir.cleanup)
    )

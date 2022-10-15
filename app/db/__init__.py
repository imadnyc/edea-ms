import os
import sys

import databases
import sqlalchemy

dbfile = 'edea-ms.sqlite'
default_db = f"sqlite:///{dbfile}"
DATABASE_URL = os.getenv("DATABASE_URL", default_db)

if "pytest" in sys.modules:
    DATABASE_URL = "sqlite:///.test.db"

metadata = sqlalchemy.MetaData()
database = databases.Database(DATABASE_URL)


def override_db(db: databases.Database):
    global database
    database = db

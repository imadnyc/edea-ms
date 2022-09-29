import os
import sys

import databases
import sqlalchemy

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///edea-ms.db")

if "pytest" in sys.modules:
    DATABASE_URL = "sqlite:///.test.db"

metadata = sqlalchemy.MetaData()
database = databases.Database(DATABASE_URL)


def override_db(db: databases.Database):
    global database
    database = db

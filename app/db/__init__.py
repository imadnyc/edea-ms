import databases
import sqlalchemy

metadata = sqlalchemy.MetaData()
database = databases.Database("sqlite:///test.db")

def override_db(db: databases.Database):
    global database
    database = db

import enum
import os
from datetime import datetime
from typing import Any

import sqlalchemy
from ormar import (
    Integer,
    ForeignKey,
    Text,
    Float,
    Model,
    ModelMeta,
    DateTime,
    JSON,
)
from sqlalchemy import func

from ..db import metadata, database, DATABASE_URL, default_db


class BaseMeta(ModelMeta):
    metadata = metadata
    database = database


class Project(Model):
    class Meta(BaseMeta):
        tablename = "projects"

    id: int | None = Integer(primary_key=True)
    number: str = Text()
    name: str = Text()


class Specification(Model):
    class Meta(BaseMeta):
        tablename = "specifications"

    id: int = Integer(primary_key=True)
    project: Project | None = ForeignKey(Project)
    name: str = Text()
    unit: str = Text()
    minimum: float = Float()
    typical: float = Float()
    maximum: float = Float()


class TestRun(Model):
    class Meta(BaseMeta):
        tablename = "testruns"

    id: int | None = Integer(primary_key=True)
    short_code: str = Text(unique=True)  # String(max_length=4)
    dut_id: str = Text()
    machine_hostname: str = Text()
    user_name: str = Text()
    test_name: str = Text()
    project: Project | None = ForeignKey(Project)
    metadata: dict[str, Any] = JSON(default={})


class MeasurementColumn(Model):
    class Meta(BaseMeta):
        tablename = "measurement_columns"

    id: int | None = Integer(primary_key=True)
    name: str = Text()
    project_id: int = Integer(nullable=False)
    project: Project | None = ForeignKey(Project, name="project_id")
    spec: Specification | None = ForeignKey(Specification)
    data_source: str | None = Text(default="")
    description: str | None = Text(default="")
    user_note: str | None = Text(default="")
    measurement_unit: str | None = Text(default="")
    flags: int | None = Integer(default=0)


class MeasurementEntry(Model):
    class Meta(BaseMeta):
        tablename = "measurement_entries"

    id: int | None = Integer(primary_key=True)
    sequence_number: int = Integer()
    testrun: TestRun | None = ForeignKey(TestRun, nullable=False)
    column: MeasurementColumn | None = ForeignKey(MeasurementColumn, nullable=False)
    numeric_value: float | None = Float(default=None, nullable=True)
    string_value: str | None = Text(default=None, nullable=True)
    created_at: datetime = DateTime(server_default=func.now())
    flags: int | None = Integer(default=0)


class ForcingCondition(Model):
    class Meta(BaseMeta):
        tablename = "forcing_conditions"

    id: int = Integer(primary_key=True)
    sequence_number: int = Integer()
    column: MeasurementColumn | None = ForeignKey(MeasurementColumn)
    numeric_value: float = Float()
    string_value: str = Text()
    testrun: TestRun | None = ForeignKey(TestRun)


class Setting(Model):
    class Meta(BaseMeta):
        tablename = "sysconfig"

    key: str = Text(primary_key=True)
    value: str = Text()


class JobState(int, enum.Enum):
    NEW = 1
    PENDING = 2
    COMPLETE = 3
    FAILED = 4


class JobQueue(Model):
    class Meta(BaseMeta):
        tablename = "jobqueue"

    id: int = Integer(primary_key=True)
    state: int = Integer(choices=list(JobState), default=JobState.NEW)
    # state: JobState = sqlalchemy.Enum(enum_class=JobState)
    worker: str = Text(default='N/A')
    updated_at: datetime = DateTime(server_default=func.now())
    function_call: str = Text()
    parameters: dict[str, Any] = JSON(default={})


# We can first create the db after the model has been defined.
if DATABASE_URL == default_db:
    dbfile = DATABASE_URL.replace('sqlite:///', '')
    if not os.path.isfile(dbfile):
        engine = sqlalchemy.create_engine(DATABASE_URL)
        metadata.create_all(engine)

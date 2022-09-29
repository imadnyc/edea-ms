from datetime import datetime

from ormar import (
    Integer,
    ForeignKey,
    Text,
    Float,
    Model,
    ModelMeta,
    DateTime,
    JSON,
    String,
)
from sqlalchemy import func

from ..db import metadata, database


class BaseMeta(ModelMeta):
    metadata = metadata
    database = database


class Project(Model):
    class Meta(BaseMeta):
        tablename = "projects"

    id: int | None = Integer(primary_key=True)
    number: int = Integer()
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
    short_code: str = String(max_length=4)
    dut_id: str = Text()
    machine_hostname: str = Text()
    user_name: str = Text()
    test_name: str = Text()
    project: Project | None = ForeignKey(Project)
    metadata: dict = JSON()


class MeasurementColumn(Model):
    class Meta(BaseMeta):
        tablename = "measurement_columns"

    id: int | None = Integer(primary_key=True)
    name: str = Text()
    project: Project | None = ForeignKey(Project)
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

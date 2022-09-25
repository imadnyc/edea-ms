from datetime import datetime
from typing import Optional

import ormar

from ..db import metadata, database


class BaseMeta(ormar.ModelMeta):
    metadata = metadata
    database = database


class Project(ormar.Model):
    class Meta(BaseMeta):
        tablename = "projects"

    id: int = ormar.Integer(primary_key=True)
    number: int = ormar.Integer()
    name: str = ormar.Text()


class Specification(ormar.Model):
    class Meta(BaseMeta):
        tablename = "specifications"

    id: int = ormar.Integer(primary_key=True)
    project: Optional[Project] = ormar.ForeignKey(Project)
    name: str = ormar.Text()
    unit: str = ormar.Text()
    minimum: float = ormar.Float()
    typical: float = ormar.Float()
    maximum: float = ormar.Float()


class TestRun(ormar.Model):
    class Meta(BaseMeta):
        tablename = "test_runs"

    id: int = ormar.Integer(primary_key=True)
    short_code: str = ormar.String(max_length=4)
    dut_id: str = ormar.Text()
    machine_hostname: str = ormar.Text()
    user_name: str = ormar.Text()
    test_name: str = ormar.Text()
    project: Optional[Project] = ormar.ForeignKey(Project)
    metadata: dict = ormar.JSON()


class MeasurementEntry(ormar.Model):
    class Meta(BaseMeta):
        tablename = "measurement_entries"

    id: int = ormar.Integer(primary_key=True)
    sequence_number: int = ormar.Integer()
    test_run_id: int = ormar.Integer()
    column_id: int = ormar.Integer()
    numeric_value: float = ormar.Float()
    string_value: str = ormar.Text()
    created_at: datetime = ormar.Time()
    flags: int = ormar.Integer()


class MeasurementColumn(ormar.Model):
    class Meta(BaseMeta):
        tablename = "measurement_columns"

    id: int = ormar.Integer(primary_key=True)
    data_source: str = ormar.Text()
    project: Optional[Project] = ormar.ForeignKey(Project)
    name: str = ormar.Text()
    description: str = ormar.Text()
    user_note: str = ormar.Text()
    spec: Optional[Specification] = ormar.ForeignKey(Specification)
    measurement_unit: str = ormar.Text()
    flags: int = ormar.Integer()


class ForcingCondition(ormar.Model):
    class Meta(BaseMeta):
        tablename = "forcing_conditions"

    id: int = ormar.Integer(primary_key=True)
    sequence_number: int = ormar.Integer()
    column: Optional[MeasurementColumn] = ormar.ForeignKey(MeasurementColumn)
    numeric_value: float = ormar.Float()
    string_value: str = ormar.Text()
    test_run: Optional[TestRun] = ormar.ForeignKey(TestRun)

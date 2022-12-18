from __future__ import annotations

import enum
from datetime import datetime
from typing import TypeVar, Any

from pydantic import BaseModel
from sqlalchemy import JSON, ForeignKey, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    relationship,
)

T = TypeVar('T', bound='Model')


class Model(DeclarativeBase):
    def update_from_model(self: T, mod: BaseModel) -> T:
        for field in mod.__fields_set__:
            if field != "id":
                setattr(self, field, getattr(mod, field))

        return self


class ProvidesProjectMixin:
    "A mixin that adds a 'project' relationship to classes."

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))

    @declared_attr
    def project(cls) -> Mapped["Project"]:
        return relationship("Project")


class ProvidesSpecificationMixin:
    "A mixin that adds a 'specification' relationship to classes."

    specification_id: Mapped[int | None] = mapped_column(ForeignKey("specifications.id"))

    @declared_attr
    def specification(cls) -> Mapped["Specification"]:
        return relationship("Specification")


class ProvidesMeasurementColumnMixin:
    "A mixin that adds a 'measurement_column' relationship to classes."

    column_id: Mapped[int] = mapped_column(ForeignKey("measurement_columns.id"))

    @declared_attr
    def column(cls) -> Mapped["MeasurementColumn"]:
        return relationship("MeasurementColumn")


class ProvidesTestRunColumnMixin:
    "A mixin that adds a 'testrun' relationship to classes."

    testrun_id: Mapped[int] = mapped_column(ForeignKey("testruns.id"))

    @declared_attr
    def testrun(cls) -> Mapped["TestRun"]:
        return relationship("TestRun")


class Project(Model):
    __tablename__: str = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str]
    name: Mapped[str]


class Specification(Model, ProvidesProjectMixin):
    __tablename__: str = "specifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    unit: Mapped[str]
    minimum: Mapped[float]
    typical: Mapped[float]
    maximum: Mapped[float]


class TestRun(Model, ProvidesProjectMixin):
    __tablename__: str = "testruns"

    id: Mapped[int] = mapped_column(primary_key=True)
    short_code: Mapped[str] = mapped_column(unique=True)  # String(max_length=4)
    dut_id: Mapped[str]
    machine_hostname: Mapped[str]
    user_name: Mapped[str]
    test_name: Mapped[str]
    data: Mapped[dict[Any, Any] | None] = mapped_column(JSON)

    __mapper_args__ = {"eager_defaults": True}


class MeasurementColumn(Model, ProvidesProjectMixin, ProvidesSpecificationMixin):
    __tablename__: str = "measurement_columns"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    data_source: Mapped[str | None] = mapped_column(default="")
    description: Mapped[str | None] = mapped_column(default="")
    user_note: Mapped[str | None] = mapped_column(default="")
    measurement_unit: Mapped[str | None] = mapped_column(default="")
    flags: Mapped[int | None] = mapped_column(default=0)


class MeasurementEntry(
    Model, ProvidesTestRunColumnMixin, ProvidesMeasurementColumnMixin
):
    __tablename__ = "measurement_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    sequence_number: Mapped[int]
    numeric_value: Mapped[float | None]
    string_value: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    flags: Mapped[int | None] = mapped_column(default=0)


class ForcingCondition(
    Model, ProvidesMeasurementColumnMixin, ProvidesTestRunColumnMixin
):
    __tablename__: str = "forcing_conditions"

    id: Mapped[int] = mapped_column(primary_key=True)
    sequence_number: Mapped[int]
    numeric_value: Mapped[float | None]
    string_value: Mapped[str | None]


class Setting(Model):
    __tablename__: str = "sysconfig"

    key: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[str]


class JobState(int, enum.Enum):
    NEW = 1
    PENDING = 2
    COMPLETE = 3
    FAILED = 4


class Job(Model):
    __tablename__: str = "jobqueue"

    id: Mapped[int] = mapped_column(primary_key=True)
    state: Mapped[JobState] = mapped_column(default=JobState.NEW)
    worker: Mapped[str] = mapped_column(default="N/A")
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now())
    function_call: Mapped[str]
    parameters: Mapped[dict[Any, Any]] = mapped_column(JSON)

    __mapper_args__ = {"eager_defaults": True}

"""SQLAlchemy ORM models (scaffold for SaaS persistence)."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    plan: Mapped[str] = mapped_column(String(50), default="free")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    birth_details: Mapped[list["BirthDetail"]] = relationship(back_populates="user")
    reports: Mapped[list["Report"]] = relationship(back_populates="user")


class BirthDetail(Base):
    __tablename__ = "birth_details"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    name: Mapped[str | None] = mapped_column(String(255))
    year: Mapped[int] = mapped_column(Integer)
    month: Mapped[int] = mapped_column(Integer)
    day: Mapped[int] = mapped_column(Integer)
    hour: Mapped[int] = mapped_column(Integer)
    minute: Mapped[int] = mapped_column(Integer)
    second: Mapped[float] = mapped_column(Float, default=0)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    timezone: Mapped[str] = mapped_column(String(64))
    place: Mapped[str | None] = mapped_column(String(255))
    ayanamsha: Mapped[str] = mapped_column(String(32), default="lahiri")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User | None] = relationship(back_populates="birth_details")
    charts: Mapped[list["Chart"]] = relationship(back_populates="birth")


class Chart(Base):
    __tablename__ = "charts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    birth_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("birth_details.id"))
    chart_type: Mapped[str] = mapped_column(String(16), default="D1")
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    birth: Mapped[BirthDetail] = relationship(back_populates="charts")


class DashaRecord(Base):
    __tablename__ = "dasha"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    birth_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("birth_details.id"))
    system: Mapped[str] = mapped_column(String(32), default="vimshottari")
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PlanetPositionRecord(Base):
    __tablename__ = "planet_positions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chart_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("charts.id"))
    planet: Mapped[str] = mapped_column(String(32))
    longitude: Mapped[float] = mapped_column(Float)
    house: Mapped[int] = mapped_column(Integer)
    extras: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class TransitRecord(Base):
    __tablename__ = "transits"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    birth_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("birth_details.id"))
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    payload: Mapped[dict] = mapped_column(JSON)


class CompatibilityRecord(Base):
    __tablename__ = "compatibility"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    boy_birth_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("birth_details.id"))
    girl_birth_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("birth_details.id"))
    total_score: Mapped[float] = mapped_column(Float)
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    birth_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("birth_details.id"))
    report_type: Mapped[str] = mapped_column(String(64), default="full")
    status: Mapped[str] = mapped_column(String(32), default="pending")
    file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User | None] = relationship(back_populates="reports")


class Remedy(Base):
    __tablename__ = "remedies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key: Mapped[str] = mapped_column(String(64), unique=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(8), default="en")


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    birth_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("birth_details.id"))
    category: Mapped[str] = mapped_column(String(64))
    language: Mapped[str] = mapped_column(String(8), default="mr")
    content: Mapped[str] = mapped_column(Text)
    provider: Mapped[str] = mapped_column(String(64), default="rule_engine")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ApiLog(Base):
    __tablename__ = "logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    path: Mapped[str] = mapped_column(String(255))
    method: Mapped[str] = mapped_column(String(16))
    status_code: Mapped[int] = mapped_column(Integer)
    duration_ms: Mapped[float] = mapped_column(Float)
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class NakshatraRecord(Base):
    __tablename__ = "nakshatras"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chart_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("charts.id"))
    body: Mapped[str] = mapped_column(String(32))
    nakshatra: Mapped[str] = mapped_column(String(64))
    pada: Mapped[int] = mapped_column(Integer)
    lord: Mapped[str] = mapped_column(String(32))
    longitude: Mapped[float] = mapped_column(Float)


class HouseCuspRecord(Base):
    __tablename__ = "houses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chart_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("charts.id"))
    system: Mapped[str] = mapped_column(String(16), default="W")
    number: Mapped[int] = mapped_column(Integer)
    cusp_longitude: Mapped[float] = mapped_column(Float)
    sign: Mapped[str] = mapped_column(String(32))
    sign_lord: Mapped[str] = mapped_column(String(32))


class DivisionalChartRecord(Base):
    __tablename__ = "divisional_charts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    birth_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("birth_details.id"))
    varga: Mapped[str] = mapped_column(String(8), index=True)
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

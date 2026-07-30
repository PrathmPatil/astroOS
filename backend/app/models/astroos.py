"""AstroOS ORM extensions — rules, evidence, classical texts, audit logs."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class ClassicalText(Base):
    __tablename__ = "classical_texts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key: Mapped[str] = mapped_column(String(64), unique=True)
    title: Mapped[str] = mapped_column(String(255))
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class Sloka(Base):
    __tablename__ = "slokas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sloka_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    text_key: Mapped[str] = mapped_column(String(64), index=True)
    chapter: Mapped[str | None] = mapped_column(String(128), nullable=True)
    sanskrit: Mapped[str | None] = mapped_column(Text, nullable=True)
    english: Mapped[str | None] = mapped_column(Text, nullable=True)
    marathi: Mapped[str | None] = mapped_column(Text, nullable=True)
    hindi: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class RuleRecord(Base):
    __tablename__ = "rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(64), index=True)
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class EvidenceRecord(Base):
    __tablename__ = "evidence"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    birth_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("birth_details.id"), nullable=True)
    conclusion_key: Mapped[str] = mapped_column(String(128), index=True)
    confidence: Mapped[float] = mapped_column(Float)
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AuditRecord(Base):
    __tablename__ = "audit_trails"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    audit_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    conclusion_key: Mapped[str] = mapped_column(String(128), index=True)
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

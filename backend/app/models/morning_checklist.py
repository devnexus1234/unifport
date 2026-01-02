from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Boolean, Index, Sequence, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.time_utils import get_ist_time


class MorningChecklist(Base):
    __tablename__ = "morning-checklist"

    id = Column(Integer, Sequence("morning_checklist_seq"), primary_key=True, index=True)
    hostname = Column("Hostname", String(255), nullable=False)
    ip = Column("IP", String(64))
    location = Column("Location", String(255))
    application_name = Column("APPLICATION_NAME", String(255), nullable=False)
    asset_status = Column("Asset_Status", String(64))
    commands = Column("Commands", String(500))
    mc_output = Column("MC_OUTPUT", Text)
    mc_group = Column("MC_GROUP", String(255))
    mc_check_date = Column("MC_CHECK_DATE", Date, nullable=False)
    mc_status = Column("MC_STATUS", String(64))
    asset_owner = Column("ASSET_OWNER", String(255))
    mc_diff_status = Column("MC_DIFF_STATUS", String(64))
    mc_criticality = Column("MC_CRITICALITY", String(64))
    updated_by = Column("UPDATED_BY", String(255))
    is_validated = Column("IS_VALIDATED", Boolean, default=False)
    updated_at = Column("UPDATED_AT", DateTime(timezone=True), default=get_ist_time, onupdate=get_ist_time)

    __table_args__ = (
        Index("idx_mc_hostname", "Hostname"),
        Index("idx_mc_check_date", "MC_CHECK_DATE"),
        Index("idx_mc_application", "APPLICATION_NAME"),
        Index("idx_mc_owner", "ASSET_OWNER"),
    )


class MorningChecklistValidation(Base):
    """Tracks validation events for hostnames."""

    __tablename__ = "morning_checklist_validations"

    id = Column(Integer, Sequence("mc_validations_seq"), primary_key=True, index=True)
    hostname = Column(String(255), nullable=False)
    application_name = Column(String(255), nullable=False)
    asset_owner = Column(String(255))
    mc_check_date = Column(Date, nullable=False)
    validated_at = Column(DateTime(timezone=True), default=get_ist_time)
    validate_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    validate_comment = Column(Text)
    mc_criticality = Column(String(64))
    is_bulk = Column(Boolean, default=False)

    validator = relationship("User", backref="validations")

    __table_args__ = (
        Index("idx_mc_validation_hostname", "hostname"),
        Index("idx_mc_validation_date", "mc_check_date"),
    )


class MorningChecklistSignOff(Base):
    """Tracks daily checklist sign-off events."""

    __tablename__ = "morning_checklist_signoff"

    id = Column(Integer, Sequence("mc_signoff_seq"), primary_key=True)
    mc_check_date = Column(Date, nullable=False, index=True)
    validate_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    validated_at = Column(DateTime(timezone=True), default=get_ist_time)
    validate_comment = Column(Text)

    validator = relationship("User", backref="signoffs")

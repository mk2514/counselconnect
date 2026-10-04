"""
Court reference table.
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Court(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Court reference entity."""

    __tablename__ = "courts"

    court_name: Mapped[str] = mapped_column(String(255), nullable=False)
    court_type: Mapped[str] = mapped_column(String(100), nullable=False)
    jurisdiction: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    authority_profiles: Mapped[list["CourtAuthorityProfile"]] = relationship(  # noqa: F821
        back_populates="court",
    )
    hearings: Mapped[list["Hearing"]] = relationship(back_populates="court")  # noqa: F821
    agendas: Mapped[list["CourtAgenda"]] = relationship(back_populates="court")  # noqa: F821

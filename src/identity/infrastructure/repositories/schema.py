from uuid import UUID
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, Uuid
from src.shared.infrastructure.db.schema import TimeStampMixin, VersionMixin
from src.shared.infrastructure.db.base import Base


class User(Base, TimeStampMixin, VersionMixin):
    """Represents user."""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    avatar: Mapped[str] = mapped_column(
        String(100), nullable=True, default="avatar/default.png"
    )
    email: Mapped[str] = mapped_column(
        String(150), unique=True, index=True, nullable=False
    )
    first_name: Mapped[str] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str] = mapped_column(String(50), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, email={self.email!r}, username={self.username!r})"

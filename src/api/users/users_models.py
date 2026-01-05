from datetime import datetime, timezone

from sqlalchemy import Integer, String, Enum, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from src.models import Base

class RoleEnum(str, enum.Enum):
    user="user"
    admin="admin"
    owner="owner"

class UserOrm(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer,primary_key=True, autoincrement=True, nullable=False)
    name: Mapped[str] = mapped_column(String,nullable=False)

    email: Mapped[str] = mapped_column(String,nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    password: Mapped[str] = mapped_column(String,nullable=False)
    role: Mapped[RoleEnum] = mapped_column(Enum(RoleEnum),nullable=False)

    projects = relationship("ProjectOrm", back_populates="owner", cascade="all, delete")

class UserOTP(Base):
    __tablename__ = "users_otp"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)

    user_id: Mapped[int] = mapped_column(Integer,ForeignKey("users.id"),nullable=False)

    # хранить created_at с таймзоной
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),  # <-- timezone=True
        default=lambda: datetime.now(tz=timezone.utc),  # <-- aware datetime
        nullable=True
    )

    hash_otp: Mapped[str] = mapped_column(String, nullable=True)

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),  # <-- timezone=True
        default=lambda: datetime.now(tz=timezone.utc),
        nullable=True
    )
    used: Mapped[bool] = mapped_column(Boolean, default=False,nullable=True)
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import ARRAY

from src.database.base import Base


class UserORM(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(100), nullable=False)
    username = Column(String(100), nullable=False)
    is_admin = Column(Boolean, default=False)
    permissions = Column(ARRAY(String(20)), default=[])
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

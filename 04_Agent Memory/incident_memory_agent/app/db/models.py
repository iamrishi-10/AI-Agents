from datetime import datetime

from sqlalchemy import DateTime, Float, Identity, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import VECTOR

from app.config.settings import EMBEDDING_DIMS
from app.db.database import Base


class Memory(Base):
    __tablename__ = "memories"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True, nullable=False)

    user_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    service_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    memory_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)

    content: Mapped[str] = mapped_column(Text, nullable=False)

    importance: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)

    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="active", index=True
    )

    embedding: Mapped[list[float]] = mapped_column(VECTOR(EMBEDDING_DIMS), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

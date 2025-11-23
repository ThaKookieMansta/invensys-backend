from db.base import Base
from sqlalchemy.orm import Mapped, mapped_column, Relationship, relationship
from sqlalchemy import String, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid




class LaptopStatus(Base):
    id: Mapped[int] = mapped_column(Integer,
                                          primary_key=True,
                                          index=True
                                    )
    status_name: Mapped[str] = mapped_column(String)

    laptops: Mapped[list["LaptopDetail"]] = relationship(
        "LaptopDetail",
        back_populates="status",
        lazy="selectin"
    )


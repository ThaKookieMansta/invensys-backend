# from db.base import Base
# from sqlalchemy.orm import Relationship, mapped_column, Mapped
# from sqlalchemy import Integer, ForeignKey
#
# class UserRole(Base):
#     id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
#     user_id: Mapped[int] = mapped_column(ForeignKey("is_user.id"))
#     role_id: Mapped[int] = mapped_column(ForeignKey("is_role.id"))

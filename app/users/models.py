from sqlalchemy import text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base, str_uniq, int_pk


class User(Base):
    id: Mapped[int_pk]
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str_uniq]
    password: Mapped[str] = mapped_column(nullable=True)

    is_admin: Mapped[bool] = mapped_column(default=False, server_default=text('false'), nullable=False)

    extend_existing = True

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"


class Log(Base):
    id: Mapped[int_pk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, user_id={self.user_id})"
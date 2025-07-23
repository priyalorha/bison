from datetime import datetime

from sqlalchemy import Integer, String, Enum, DateTime
from sqlalchemy.orm import relationship, mapped_column, Mapped
from models.base import Base
import constants


class LoginCred(Base):
    __tablename__ = 'login_credentials'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    provider = mapped_column(Enum(constants.Provider), nullable=False)
    username = mapped_column(String, nullable=False, unique=True)
    password = mapped_column(String, nullable=False)

    session_token: Mapped["IChartSessionToken"] = relationship(
        "IChartSessionToken",  # 👈 as a string
        back_populates="login_cred",
        uselist=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow,
                                                 onupdate=datetime.utcnow)

    # session_token: Mapped["IChartSessionToken"] = relationship(back_populates="login_cred")

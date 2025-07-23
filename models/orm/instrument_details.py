from sqlalchemy import String, Boolean, Integer, Enum, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship

import constants
from models.base import Base

# class Instruments(Base):
#     __tablename__ = 'instruments'
#     id: Mapped[int] = mapped_column(Integer,primary_key=True, autoincrement=True)
#     name: Mapped[str] = mapped_column(String, nullable=False)
#     symbol: Mapped[str] = mapped_column(String, nullable=False)
#     exchange: Mapped[constants.Exchange] = mapped_column(Enum(constants.Exchange), nullable=False)
#     segment: Mapped[constants.Segment] = mapped_column(Enum(constants.Segment), nullable=False)


from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from typing import List
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base
import constants


class InstrumentDetails(Base):
    __tablename__ = 'instrument_details'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    instrument_name: Mapped[str] = mapped_column(nullable=False)
    instrument_contract: Mapped[str] = mapped_column(nullable=False, unique=True)
    exchange: Mapped[constants.Exchange] = mapped_column(nullable=False)
    segment: Mapped[constants.Segment] = mapped_column(nullable=False)
    instrument_type: Mapped[constants.InstrumentType] = mapped_column(nullable=False)
    latest: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow,
                                                 onupdate=datetime.utcnow)

    # Use string reference for forward declaration
    min_data: Mapped[List["MinOHLCV"]] = relationship(
        "MinOHLCV",
        back_populates="instrument",
        cascade="all, delete-orphan"
    )

    _table_args__ = (
        UniqueConstraint('instrument_contract', 'exchange', 'segment', 'instrument_type', name='uq_symbol_exchange'),
    )

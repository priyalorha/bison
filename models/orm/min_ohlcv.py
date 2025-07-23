from datetime import datetime

from sqlalchemy import Numeric, ForeignKey, BigInteger, DateTime, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship

from models.base import Base


class MinOHLCV(Base):
    __tablename__ = 'min_ohlcv'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    instrument_id: Mapped[str] = mapped_column(ForeignKey("instrument_details.instrument_contract"))
    timestamp: Mapped[int] = mapped_column(BigInteger, nullable=False)
    open: Mapped[float] = mapped_column(Numeric, nullable=False)
    high: Mapped[float] = mapped_column(Numeric, nullable=False)
    low: Mapped[float] = mapped_column(Numeric, nullable=False)
    close: Mapped[float] = mapped_column(Numeric, nullable=False)
    volume: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow,
                                                 onupdate=datetime.utcnow)

    # Consistent naming with InstrumentDetails
    instrument: Mapped["InstrumentDetails"] = relationship(
        "InstrumentDetails",
        back_populates="min_data"
    )

    __table_args__ = (
        UniqueConstraint( 'instrument_id', 'timestamp', name='_min_ohlvc_unique'),
    )


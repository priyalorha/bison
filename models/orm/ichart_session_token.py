from datetime import datetime, time

from sqlalchemy import Integer, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship, mapped_column, Mapped

from constants import KOLKATA_TZ
from models.base import Base


class IChartSessionToken(Base):
    __tablename__ = 'ichart_session_tokens'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[str] = mapped_column(String, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_in: Mapped[int] = mapped_column(Integer, default=86400)

    login_cred_id: Mapped[int] = mapped_column(ForeignKey("login_credentials.id"))  # ✅ exact table name
    login_cred: Mapped["LoginCred"] = relationship(back_populates="session_token")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow,
                                                 onupdate=datetime.utcnow)

    @property
    def expires_at(self) -> datetime:
        if not self.generated_at:
            return None

        if self.generated_at.tzinfo is None:
            localized_generated_at = KOLKATA_TZ.localize(self.generated_at)
        else:
            localized_generated_at = self.generated_at.astimezone(KOLKATA_TZ)

        end_of_day_kolkata = datetime.combine(localized_generated_at.date(), time.max, tzinfo=KOLKATA_TZ)
        return end_of_day_kolkata

    @property
    def is_expired(self) -> bool:
        if not self.expires_at:
            return True

        current_time_kolkata = datetime.now(KOLKATA_TZ)

        return current_time_kolkata >= self.expires_at

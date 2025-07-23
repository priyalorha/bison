from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import csv

@dataclass
class IcRespOptDataRecord:
    """Represents option contract time-series data"""
    datetime: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    open_interest: int
    atp: Optional[float] = None  # Average Trade Price (nullable)
    add_field1: Optional[float] = None
    add_field2: Optional[float] = None

    # Custom datetime format for CSV
    DATETIME_FORMAT = "%d.%m.%y %H:%M:%S"  # Matches common iCharts format

    def to_csv_row(self) -> list:
        """Converts record to CSV row with proper formatting"""
        return [
            self.datetime.strftime(self.DATETIME_FORMAT),
            f"{self.open:.2f}",
            f"{self.high:.2f}",
            f"{self.low:.2f}",
            f"{self.close:.2f}",
            str(self.volume),
            str(self.open_interest),
            f"{self.atp:.2f}" if self.atp is not None else "",
            f"{self.add_field1:.2f}" if self.add_field1 is not None else "",
            f"{self.add_field2:.2f}" if self.add_field2 is not None else ""
        ]

    @classmethod
    def get_csv_header(cls) -> list[str]:
        """Returns CSV header matching iCharts format"""
        return [
            "DateTime", "Open", "High", "Low", "Close",
            "Volume", "OpenInterest", "ATP", "AddField1", "AddField2"
        ]

    @classmethod
    def from_csv_row(cls, row: dict):
        """Creates record from CSV row with type conversion"""
        return cls(
            datetime=datetime.strptime(row["DateTime"], cls.DATETIME_FORMAT),
            open=float(row["Open"]),
            high=float(row["High"]),
            low=float(row["Low"]),
            close=float(row["Close"]),
            volume=int(row["Volume"]),
            open_interest=int(row["OpenInterest"]),
            atp=float(row["ATP"]) if row["ATP"] else None,
            add_field1=float(row["AddField1"]) if row["AddField1"] else None,
            add_field2=float(row["AddField2"]) if row["AddField2"] else None
        )
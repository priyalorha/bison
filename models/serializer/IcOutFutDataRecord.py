from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import csv

@dataclass
class IcOutFutDataRecord:
    ticker: str
    date: datetime
    time: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    eq_symbol: str
    expiry_date: datetime
    open_interest: int  # Open Interest
    atp: float         # Average Trade Price
    add_field1: float  # TotalValue

    def to_csv_row(self) -> list:
        """Converts record to a CSV row with proper formatting"""
        return [
            self.ticker,
            self.date.strftime("%Y-%m-%d"),
            self.time,
            str(self.open),
            str(self.high),
            str(self.low),
            str(self.close),
            str(self.volume),
            self.eq_symbol,
            self.expiry_date.strftime("%Y-%m-%d"),
            str(self.open_interest),
            str(self.atp),
            str(self.add_field1)
        ]

    @classmethod
    def get_csv_header(cls) -> list[str]:
        """Returns CSV header row"""
        return [
            "Ticker", "Date", "Time", "Open", "High", "Low", "Close",
            "Volume", "EqSymbol", "ExpiryDate", "OpenInterest", "ATP", "AddField1"
        ]

    @classmethod
    def write_to_csv(cls, records: list['IcOutFutDataRecord'], file_path: str):
        """Writes multiple records to CSV file"""
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(cls.get_csv_header())
            for record in records:
                writer.writerow(record.to_csv_row())

    @classmethod
    def read_from_csv(cls, file_path: str) -> list['IcOutFutDataRecord']:
        """Reads records from CSV file"""
        records = []
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                records.append(cls(
                    ticker=row['Ticker'],
                    date=datetime.strptime(row['Date'], "%Y-%m-%d"),
                    time=row['Time'],
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    volume=int(row['Volume']),
                    eq_symbol=row['EqSymbol'],
                    expiry_date=datetime.strptime(row['ExpiryDate'], "%Y-%m-%d"),
                    open_interest=int(row['OpenInterest']),
                    atp=float(row['ATP']),
                    add_field1=float(row['AddField1'])
                ))
        return records
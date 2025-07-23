from dataclasses import dataclass
from datetime import datetime
import csv

@dataclass
class IcOutOptDataRecord:
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
    strike: str
    option_type: str
    open_interest: int  # Open Interest
    atp: float         # Average Traded Price
    add_field1: float
    add_field2: float

    def to_csv_row(self) -> list:
        """Converts record to a CSV row with proper formatting"""
        return [
            self.ticker,
            self.date.strftime("%Y-%m-%d"),
            self.time,
            f"{self.open:.2f}",
            f"{self.high:.2f}",
            f"{self.low:.2f}",
            f"{self.close:.2f}",
            str(self.volume),
            self.eq_symbol,
            self.expiry_date.strftime("%Y-%m-%d"),
            self.strike,
            self.option_type,
            str(self.open_interest),
            f"{self.atp:.2f}",
            f"{self.add_field1:.2f}",
            f"{self.add_field2:.2f}"
        ]

    @classmethod
    def get_csv_header(cls) -> list[str]:
        """Returns CSV header row matching C# class structure"""
        return [
            "Ticker", "Date", "Time", "Open", "High", "Low", "Close",
            "Volume", "EqSymbol", "ExpiryDate", "Strike", "OptionType",
            "OpenInterest", "ATP", "AddField1", "AddField2"
        ]

    @classmethod
    def write_to_csv(cls, records: list['IcOutOptDataRecord'], file_path: str):
        """Writes multiple records to CSV file"""
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(cls.get_csv_header())
            for record in records:
                writer.writerow(record.to_csv_row())

    @classmethod
    def read_from_csv(cls, file_path: str) -> list['IcOutOptDataRecord']:
        """Reads records from CSV file with proper type conversion"""
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
                    strike=row['Strike'],
                    option_type=row['OptionType'],
                    open_interest=int(row['OpenInterest']),
                    atp=float(row['ATP']),
                    add_field1=float(row['AddField1']),
                    add_field2=float(row['AddField2'])
                ))
        return records
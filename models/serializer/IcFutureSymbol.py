from dataclasses import dataclass
from enum import Enum

# First, let's define the enums for type safety (optional but recommended)
class IcExchange(str, Enum):
    NSE = "NSE"
    BSE = "BSE"
    NEW = "NEW"

class IcSegment(str, Enum):
    INDEX = "Index"
    STOCK = "Stock"
    CURRENCY = "Currency"
    NEW = "New"

@dataclass
class IcFutureSymbol:
    symbol: str
    exchange: IcExchange  # Using enum for type safety
    segment: IcSegment   # Using enum for type safety

    # If you want to maintain string compatibility like C#
    def __post_init__(self):
        # Convert string inputs to enums if needed
        if isinstance(self.exchange, str):
            self.exchange = IcExchange(self.exchange.upper())
        if isinstance(self.segment, str):
            self.segment = IcSegment(self.segment.capitalize())
from enum import Enum, auto
from dataclasses import dataclass

class IcSegment(Enum):
    INDEX = auto()
    STOCK = auto()
    CURRENCY = auto()
    NEW = auto()

class IcExchange(Enum):
    NSE = auto()
    BSE = auto()
    NEW = auto()

class IcInstrumentType(Enum):
    FUTURE = auto()
    OPTION = auto()

@dataclass
class IcEnums:
    """Empty dataclass equivalent to C# IcEnums class"""
    pass
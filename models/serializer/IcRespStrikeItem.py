from dataclasses import dataclass
from typing import Optional
import json

@dataclass
class IcRespStrikeItem:
    id: str  # Strike price as string (e.g., "20000")
    name: str  # Display name (often same as strike price)

    @classmethod
    def from_json(cls, json_str: str) -> list['IcRespStrikeItem']:
        """Creates list of strike items from JSON response"""
        try:
            data = json.loads(json_str)
            return [cls(id=str(item["id"]), name=str(item["name"])) for item in data]
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid strike data format: {e}")

    def to_dict(self) -> dict:
        """Converts back to dictionary for JSON serialization"""
        return {"id": self.id, "name": self.name}
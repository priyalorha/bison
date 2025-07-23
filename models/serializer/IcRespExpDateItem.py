from dataclasses import dataclass
import json
from typing import List
from datetime import datetime


@dataclass
class IcRespExpDateItem:
    """Represents an expiry date item from iCharts API response"""
    id: str  # The expiry date in format like "28AUG24"

    @classmethod
    def parse_expiry_dates(cls, json_response: str) -> List['IcRespExpDateItem']:
        """
        Parses the iCharts API response containing expiry dates
        Example JSON format: [{"id":"28AUG24"},{"id":"26SEP24"}]
        """
        try:
            # The iCharts API returns a JSON array where the first element contains the dates
            outer_list = json.loads(json_response)
            if not outer_list or not isinstance(outer_list, list):
                return []

            # The actual date items are in the first element of the outer array
            date_items = json.loads(outer_list[0])
            return [cls(id=item["id"]) for item in date_items]
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            raise ValueError(f"Failed to parse expiry dates: {e}")

    def to_expiry_date(self) -> datetime:
        """Converts the ID string to a proper datetime object"""
        from datetime import datetime
        try:
            return datetime.strptime(self.id, "%d%b%y")
        except ValueError as e:
            raise ValueError(f"Invalid expiry date format '{self.id}': {e}")
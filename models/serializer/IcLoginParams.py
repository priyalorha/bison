from dataclasses import dataclass
from datetime import datetime

@dataclass
class IcLoginParams:
    user_id: str
    password: str
    subscription_expiry: datetime

    # Optional: Add input validation
    def __post_init__(self):
        if not self.user_id:
            raise ValueError("User ID cannot be empty")
        if not self.password:
            raise ValueError("Password cannot be empty")
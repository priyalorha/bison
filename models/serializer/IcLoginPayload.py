from dataclasses import dataclass

@dataclass
class IcLoginPayload:
    username: str
    password: str
    php_sess_id: str = ""
    submit: str = "Login"  # Default value matching C# behavior

    def to_dict(self) -> dict:
        """Converts the payload to a dictionary for HTTP requests"""
        return {
            "username": self.username,
            "password": self.password,
            "PHPSESSID": self.php_sess_id,
            "submit": self.submit
        }
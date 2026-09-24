from dataclasses import dataclass


@dataclass
class SignUpRequest:
    login: str
    password: str

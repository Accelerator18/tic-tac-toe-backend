from dataclasses import dataclass


@dataclass
class SignUpRequestDto:
    login: str
    password: str

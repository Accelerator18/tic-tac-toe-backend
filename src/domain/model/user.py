from dataclasses import dataclass


@dataclass
class User:
    uuid: str
    login: str
    password_hash: str

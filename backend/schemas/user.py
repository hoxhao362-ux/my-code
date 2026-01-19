from dataclasses import dataclass

@dataclass
class UserAccount:
    __slots__ = [
        "uid",
        "uid_hash",
        "username",
        "password",
        "email",
        "create_time",
        "last_login_time",
        "is_admin",
    ]
    uid: int
    uid_hash: str
    username: str
    password: str
    email: str
    create_time: str
    last_login_time: str
    is_admin: bool
    

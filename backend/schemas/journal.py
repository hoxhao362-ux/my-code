from dataclasses import dataclass

@dataclass
class Eassy:
    __slots__ = [
        "jid",
        "file_hash",
        "title",
        "upload_time",
        "writer",
        "team",
        "read_permission",
        "read_count",
    ]
    jid: int
    file_hash: str
    title: str
    upload_time: str
    writer: list[str]
    team: str | None = None
    read_permission: str = "public"
    read_count: int = 0
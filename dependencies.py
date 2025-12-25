from dataclasses import dataclass


@dataclass
class MyDeps:
    db_name: str
    is_admin: bool

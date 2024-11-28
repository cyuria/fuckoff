from dataclasses import dataclass


@dataclass
class ShellConfiguration:
    content: str
    path: str
    reload: str
    can_configure_automatically: bool

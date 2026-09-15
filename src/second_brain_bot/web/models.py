from dataclasses import dataclass


@dataclass(frozen=True)
class WebSource:
    title: str
    url: str
    content: str
import json
from typing import Optional


def load_all_links() -> dict[str, str]:
    with open("files/links.json", "r") as file:
        return json.load(file)


def get_link_for(name: str) -> Optional[str]:
    links = load_all_links()
    for link in links:
        if link.lower() == name.lower():
            return links[link]

    return None

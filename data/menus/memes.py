from dataclasses import dataclass, field

from data.menus.paginated import Paginated
from functions import stringFormatters
from functions.database import memes


@dataclass
class MemesList(Paginated):
    title: str = field(default="Memes")

    def __post_init__(self):
        self.data = self.get_data()

    def get_data(self) -> list[tuple]:
        data = []
        meme_list = memes.getAllMemes()
        for meme in sorted(meme_list, key=lambda x: x[1]):
            name = stringFormatters.title_case(meme[1])
            fields = meme[2]
            data.append((name, fields,))

        return data

    def format_entry(self, index: int, value: tuple) -> str:
        return f"{value[0]} ({value[1]})"

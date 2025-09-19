from dataclasses import dataclass
from PIL.Image import Image as PILImageType
from pathlib import Path


@dataclass
class Card:
    copies: int
    slots: list

    name: str
    id: str
    has_bleed: bool
    image_path: Path
    image: PILImageType|None = None
    has_image: bool = False

    def __repr__(self) -> str:
        return self.name

    def set_image(self, image: PILImageType) -> None:
        self.image = image
        self.has_image = True

    def __floordiv__(self, other: 'Card|None') -> 'DoubleSidedCard':
        return DoubleSidedCard(front=self, back=other)


class DoubleSidedCard:
    def __init__(self, front: Card, back: Card|None = None) -> None:
        self.front = front
        self.back = back
        self.slots = self.front.slots
        self.copies = self.front.copies


    def __repr__(self):
        if self.back is None:
            return self.front.name
        else:
            return f'{self.front.name} // {self.back.name}'



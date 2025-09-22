from dataclasses import dataclass
from PIL.Image import Image as PILImageType
from pathlib import Path


@dataclass
class Card:
    '''
    Simple data class for containing card information. Makes no distinction
    between card fronts and card backs. 

    Attributes:
        copies (int):              Number of copies of this card to be included in the project.
        slots (list[str]):         Slot(s) that this card occupies from MPCFill project, crucial 
                                   for matching to back sides.
        name (str):                Name of card.
        id (str):                  Google Drive ID for card image.
        has_bleed (bool):          True if card has extra space around card; true of all MPCFill
                                   images, assumed False otherwise.
        image_path (Path):         Path to image on disk
        image (PILImageType|None): Card image, usually set after instansiation.
        has_image (bool):          True if image has been set.
    '''
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
    '''
    Represents a physical card with front and an optional back, encapsulating both sides into a single
    object.
    
    Attributes:
        front (Card):            Front side of card
        back (Card|None):        Back side of card, can be None for single-sided cards.
        slots (list[str]):       Slot(s) that this card occupies from MPCFill, inherited from front
        copies (int):            Number of copies of this card to be included in the project, inherited 
                                 from front.
        has_generic_back (bool): True if back is a generic card back.
    '''
    def __init__(self, front: Card, back: Card|None = None) -> None:
        self.front = front
        self.back = back

        self.slots = self.front.slots
        self.copies = self.front.copies
        self.has_generic_back = False

    def __repr__(self):
        if self.back is None:
            return self.front.name
        else:
            return f'{self.front.name} // {self.back.name}'



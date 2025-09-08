from dataclasses import dataclass
from PIL.Image import Image as PILImageType
from pathlib import Path

@dataclass
class Card:
    """Container for card information, extracted from .xml file."""
    instances: int
    slots: list

    #---- Front ----
    name: str
    id: str
    has_bleed: bool
    image_path: Path
    image: PILImageType|None = None
    has_image: bool = False

    #---- Back ----
    name_back: str = ""
    id_back: str = ""
    has_bleed_back: bool = False
    image_path_back: Path = Path()
    image_back: PILImageType|None = None
    has_image_back: bool = False
    has_back: bool = False


    def set_image(self, image: PILImageType, image_back: PILImageType|None = None) -> 'Card':
        params = self.__dict__
        params["image"] = image
        params["has_image"] = True

        if image_back is not None:
            params["image_back"] = image_back
            params["has_image_back"] = True

        return Card(**params)


    def __repr__(self):
        if self.has_back:
            return f"{self.name} // {self.name_back}"
        else:
            return f"{self.name}"


    def __floordiv__(self, other: 'Card') -> 'Card':
        return Card(
            instances=self.instances,
            slots=self.slots,
            name=self.name,
            id=self.id,
            has_bleed=self.has_bleed,
            image_path=self.image_path,
            image=self.image,

            name_back=other.name,
            id_back=other.id,
            has_bleed_back=other.has_bleed,
            image_path_back=other.image_path,
            image_back=other.image,

            has_back=True
        )

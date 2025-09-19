from src.card import Card
from pathlib import Path

import xml.etree.ElementTree as ET

import src.params as params

class CardParser:
    def __init__(self, card_data: ET.Element) -> None:
        self.card_xml = card_data

    def extract_card(self) -> Card:
        card = Card(
            name=self.get_name(),
            id=self.get_id(),
            slots=self.get_slots(),
            copies=self.get_copies(),
            has_bleed=self.has_bleed(),
            image_path=self.get_image_path()
        )

        return card

    def get_id(self) -> str:
        id = self.card_xml.findtext("id")
        if id is None:
            raise Exception(f"ID missing from {self.get_name()}")
        return id

    def get_name(self) -> str:
        name = self.card_xml.findtext("query")
        if name is None:
            raise Exception("A card is missing query data")
        return name.title()

    def get_slots(self) -> list[str]:
        slots = self.card_xml.findtext("slots")
        if slots is None:
            raise Exception(f"Slots data missing from {self.get_name()}")
        return slots.split(",")

    def get_copies(self) -> int:
         return len(self.get_slots())

    def has_bleed(self) -> bool:
        #Non MPCFill cards should be marked with an id made only of
        #x. It is assumed that such a card has no bleed.
        if set(self.get_id()) == set("x"):
            return False
        return True

    def get_image_path(self) -> Path:
        image_name = self.card_xml.findtext("name")
        if image_name is None:
            raise Exception(f"Name data missing from {self.get_name()}")


        image_stem = Path(image_name).stem
        image_ext = Path(image_name).suffix

        id = self.get_id()
        if set(id) == set("x"):
            return params.CUSTOM_IMAGE_PATH / f"{image_stem}{image_ext}"
        else:
            return params.IMAGE_PATH / f"{image_stem} ({id}){image_ext}"

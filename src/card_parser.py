from src.card import Card
from pathlib import Path

import src.params as params

class CardParser:
    def __init__(self, card_data):
        self.card_xml = card_data

    def extract_card(self) -> Card:
        card = Card(
            name=self.get_name(),
            id=self.get_id(),
            slots=self.get_slots(),
            instances=self.get_instances(),
            has_bleed=self.has_bleed(),
            image_path=self.get_image_path()
        )
        return card

    def get_id(self) -> str:
        id = self.card_xml.find("id")
        if id is not None:
            return self.card_xml.find("id").text
        else:
            raise Exception("ID missing")

    def get_name(self) -> str:
         return self.card_xml.find("query").text.title()

    def get_slots(self) -> list[str]:
        return self.card_xml.find("slots").text.split(",")

    def get_instances(self) -> int:
         return len(self.get_slots())

    def has_bleed(self) -> bool:
        #Non MPCFill cards should be marked with an id made only of
        #x. It is assumed that such a card has no bleed.
        if set(self.get_id()) == set("x"):
            return False
        return True

    def get_image_path(self) -> Path:
        image_name = Path(self.card_xml.find("name").text).stem
        image_ext = Path(self.card_xml.find("name").text).suffix
        id = self.get_id()
        if set(id) == set("x"):
            return params.CUSTOM_IMAGE_PATH / f"{image_name}{image_ext}"
        else:
            return params.IMAGE_PATH / f"{image_name} ({id}){image_ext}"

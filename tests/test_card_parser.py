import unittest
from src.card_parser import CardParser
from pathlib import Path
import src.params as params
import tests.mock_xmls as mock_xmls

class TestCardParser(unittest.TestCase):
    def setUp(self):
        self.test_xml = mock_xmls.MockXMLs().xml_sol_ring()
        self.test_xml_back = mock_xmls.MockXMLs().xml_black_lotus()
        self.test_xml_custom = mock_xmls.MockXMLs().xml_custom_card()

    def test_get_id(self):
        self.assertEqual(CardParser(self.test_xml).get_id(), "1234abcd")

    def test_get_name(self):
        self.assertEqual(CardParser(self.test_xml).get_name(), "Sol Ring")

    def test_get_slots(self):
        self.assertEqual(CardParser(self.test_xml).get_slots(), ['1', '2', '3'])

    def test_get_instances(self):
        self.assertEqual(CardParser(self.test_xml).get_copies(), 3)
        self.assertEqual(CardParser(self.test_xml_back).get_copies(), 1)

    def test_has_bleed(self):
        self.assertEqual(CardParser(self.test_xml).has_bleed(), True)
        self.assertEqual(CardParser(self.test_xml_custom).has_bleed(), False)

    def test_get_image_path(self):
        self.assertEqual(CardParser(self.test_xml).get_image_path(), params.IMAGE_PATH / "Sol Ring (Cool Image) [MH3] (1234abcd).png")

    def test_extract_card(self):
        card = CardParser(self.test_xml).extract_card()
        self.assertEqual(card.name, "Sol Ring")
        self.assertEqual(card.id, "1234abcd")
        self.assertEqual(card.slots, ['1', '2', '3'])
        self.assertEqual(card.copies, 3)
        self.assertEqual(card.has_bleed, True)
        self.assertEqual(card.image_path, params.IMAGE_PATH / "Sol Ring (Cool Image) [MH3] (1234abcd).png")

    def test_combine_card(self):
        card_front = CardParser(self.test_xml).extract_card()
        card_back = CardParser(self.test_xml_back).extract_card()

        card = card_front // card_back

        self.assertEqual(card.front.name, "Sol Ring")
        self.assertEqual(card.front.id, "1234abcd")
        self.assertEqual(card.slots, ['1', '2', '3'])
        self.assertEqual(card.copies, 3)
        self.assertEqual(card.front.has_bleed, True)
        self.assertEqual(card.front.image_path, params.IMAGE_PATH / "Sol Ring (Cool Image) [MH3] (1234abcd).png")
        self.assertEqual(card.back.id, "4567efgh") 
        self.assertEqual(card.back.name, "Black Lotus") 
        self.assertEqual(card.back.has_bleed, True) 
        self.assertEqual(card.back.image_path, params.IMAGE_PATH / "Black Lotus [alpha] (4567efgh).jpg") 


if __name__ == "__main__":
    unittest.main()

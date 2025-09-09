import unittest
from src.card_parser import CardParser
from pathlib import Path
import src.params as params
import tests.mock_xmls as mock_xmls

class TestCardParser(unittest.TestCase):
    def setUp(self):
        self.test_xml = mock_xmls.xml_sol_ring()
        self.test_xml_back = mock_xmls.xml_black_lotus()
        self.test_xml_custom = mock_xmls.xml_custom_card()

    def test_get_id(self):
        self.assertEqual(CardParser(self.test_xml).get_id(), "1234abcd")

    def test_get_name(self):
        self.assertEqual(CardParser(self.test_xml).get_name(), "Sol Ring")

    def test_get_slots(self):
        self.assertEqual(CardParser(self.test_xml).get_slots(), ['1', '2', '3'])

    def test_get_instances(self):
        self.assertEqual(CardParser(self.test_xml).get_instances(), 3)
        self.assertEqual(CardParser(self.test_xml_back).get_instances(), 1)

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
        self.assertEqual(card.instances, 3)
        self.assertEqual(card.has_bleed, True)
        self.assertEqual(card.image_path, params.IMAGE_PATH / "Sol Ring (Cool Image) [MH3] (1234abcd).png")

    def test_combine_card(self):
        card_front = CardParser(self.test_xml).extract_card()
        card_back = CardParser(self.test_xml_back).extract_card()

        self.assertEqual(card_front.id_back, "") 
        self.assertEqual(card_front.name_back, "") 
        self.assertEqual(card_front.has_bleed_back, False) 
        self.assertEqual(card_front.image_path_back, Path()) 
        self.assertEqual(card_front.has_back, False)

        card = card_front // card_back

        self.assertEqual(card.name, "Sol Ring")
        self.assertEqual(card.id, "1234abcd")
        self.assertEqual(card.slots, ['1', '2', '3'])
        self.assertEqual(card.instances, 3)
        self.assertEqual(card.has_bleed, True)
        self.assertEqual(card.image_path, params.IMAGE_PATH / "Sol Ring (Cool Image) [MH3] (1234abcd).png")
        self.assertEqual(card.id_back, "4567efgh") 
        self.assertEqual(card.name_back, "Black Lotus") 
        self.assertEqual(card.has_bleed_back, True) 
        self.assertEqual(card.image_path_back, params.IMAGE_PATH / "Black Lotus [alpha] (4567efgh).jpg") 
        self.assertEqual(card.has_back, True)

if __name__ == "__main__":
    unittest.main()

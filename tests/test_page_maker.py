import unittest
from pathlib import Path
import src.page_maker
import tests.mock_xmls
from unittest.mock import MagicMock, patch

class TestGetCardsInfoFromXML(unittest.TestCase):
    def custom_open(self, filename):
        mock_file = MagicMock()
        mock_file.__enter__.return_value = getattr(tests.mock_xmls.MockXMLs(), str(filename))()
        return mock_file


    def test_2_fronts_1_back_generic_back(self):
        with patch('builtins.open', self.custom_open):
            fronts, backs, generic_back = src.page_maker.get_cards_info_from_xml(Path('xml_2fronts_1backs_generic_back'))

        self.assertEqual(len(fronts), 2)
        self.assertEqual(len(backs), 1)

        self.assertEqual(fronts[0].id, '1234abcd')
        self.assertEqual(fronts[1].slots, ['4'])
        self.assertEqual(backs[0].name, 'Black Lotus')
        self.assertEqual(generic_back.slots, ['-1'])


    def test_2_fronts_0_back_generic_back(self):
        with patch('builtins.open', self.custom_open):
            fronts, backs, generic_back = src.page_maker.get_cards_info_from_xml(Path('xml_2fronts_0backs_generic_back'))

        self.assertEqual(len(fronts), 2)
        self.assertEqual(len(backs), 0)

        self.assertEqual(fronts[0].id, '1234abcd')
        self.assertEqual(fronts[1].slots, ['4'])
        self.assertEqual(backs, [])
        self.assertEqual(generic_back.id, '1LrVx2978_dkj')


    def test_empty(self):
        with self.assertRaises(Exception):
            with patch('builtins.open', self.custom_open):
                fronts, backs, generic_back = src.page_maker.get_cards_info_from_xml(Path('xml_empty'))




if __name__ == '__main__':
    unittest.main()

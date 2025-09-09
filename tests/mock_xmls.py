import xml.etree.ElementTree as ET
import io

def make_filelike(xml):
    xml_bytes = ET.tostring(xml, encoding='utf-8')
    return io.StringIO(xml_bytes.decode('utf-8'))

def xml_2fronts_1backs_generic_back():
    xml = ET.Element("order")
    fronts = ET.SubElement(xml, "fronts")
    card1 = ET.SubElement(fronts, "card")
    ET.SubElement(card1, "id").text = "1234abcd"
    ET.SubElement(card1, "slots").text = "1,2,3"
    ET.SubElement(card1, "name").text = "Sol Ring (Cool Image) [MH3].png"
    ET.SubElement(card1, "query").text = "sol ring"

    card2 = ET.SubElement(fronts, "card")
    ET.SubElement(card2, "id").text = "4567efgh"
    ET.SubElement(card2, "slots").text = "4"
    ET.SubElement(card2, "name").text = "Black Lotus [alpha].jpg"
    ET.SubElement(card2, "query").text = "black lotus"

    backs = ET.SubElement(xml, "backs")

    card_back = ET.SubElement(backs, "card")
    ET.SubElement(card_back, "id").text = "18938GGD18"
    ET.SubElement(card_back, "slots").text = "4"
    ET.SubElement(card_back, "name").text = "Back Card.jpg"
    ET.SubElement(card_back, "query").text = "back card"

    ET.SubElement(xml, "cardback").text = "1LrVx2978_dkj"

    return xml

def xml_2fronts_0backs_generic_back():
    xml = ET.Element("order")
    fronts = ET.SubElement(xml, "fronts")
    card1 = ET.SubElement(fronts, "card")
    ET.SubElement(card1, "id").text = "1234abcd"
    ET.SubElement(card1, "slots").text = "1,2,3"
    ET.SubElement(card1, "name").text = "Sol Ring (Cool Image) [MH3].png"
    ET.SubElement(card1, "query").text = "sol ring"

    card2 = ET.SubElement(fronts, "card")
    ET.SubElement(card2, "id").text = "4567efgh"
    ET.SubElement(card2, "slots").text = "4"
    ET.SubElement(card2, "name").text = "Black Lotus [alpha].jpg"
    ET.SubElement(card2, "query").text = "black lotus"

    ET.SubElement(xml, "cardback").text = "1LrVx2978_dkj"

    return xml

def xml_empty():
    return ET.Element("")

def xml_sol_ring():
    xml = ET.Element("card")
    ET.SubElement(xml, "id").text = "1234abcd"
    ET.SubElement(xml, "slots").text = "1,2,3"
    ET.SubElement(xml, "name").text = "Sol Ring (Cool Image) [MH3].png"
    ET.SubElement(xml, "query").text = "sol ring"
    return xml

def xml_black_lotus():
    xml = ET.Element("card")
    ET.SubElement(xml, "id").text = "4567efgh"
    ET.SubElement(xml, "slots").text = "4"
    ET.SubElement(xml, "name").text = "Black Lotus [alpha].jpg"
    ET.SubElement(xml, "query").text = "black lotus"
    return xml

def xml_custom_card():
    xml = ET.Element("card")
    ET.SubElement(xml, "id").text = "xxxx"
    ET.SubElement(xml, "slots").text = "1000"
    ET.SubElement(xml, "name").text = "i_win_wotc.jpg"
    ET.SubElement(xml, "query").text = "i_win_wotc"
    return xml


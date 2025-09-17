import xml.etree.ElementTree as ET
import io

class MockXMLs():

    @staticmethod
    def make_filelike(xml):
        xml_bytes = ET.tostring(xml, encoding='utf-8')
        return io.StringIO(xml_bytes.decode('utf-8'))


    def xml_sol_ring(self):
        xml = ET.Element("card")
        ET.SubElement(xml, "id").text = "1234abcd"
        ET.SubElement(xml, "slots").text = "1,2,3"
        ET.SubElement(xml, "name").text = "Sol Ring (Cool Image) [MH3].png"
        ET.SubElement(xml, "query").text = "sol ring"
        return xml


    def xml_black_lotus(self):
        xml = ET.Element("card")
        ET.SubElement(xml, "id").text = "4567efgh"
        ET.SubElement(xml, "slots").text = "4"
        ET.SubElement(xml, "name").text = "Black Lotus [alpha].jpg"
        ET.SubElement(xml, "query").text = "black lotus"
        return xml


    def xml_custom_card(self):
        xml = ET.Element("card")
        ET.SubElement(xml, "id").text = "xxxx"
        ET.SubElement(xml, "slots").text = "1000"
        ET.SubElement(xml, "name").text = "i_win_wotc.jpg"
        ET.SubElement(xml, "query").text = "i_win_wotc"
        return xml


    def xml_2fronts_1backs_generic_back(self):
        xml = ET.Element("order")

        fronts = ET.SubElement(xml, "fronts")
        fronts.append(self.xml_sol_ring())
        fronts.append(self.xml_black_lotus())


        backs = ET.SubElement(xml, "backs")
        backs.append(self.xml_black_lotus())

        ET.SubElement(xml, "cardback").text = "1LrVx2978_dkj"

        return self.make_filelike(xml)


    def xml_2fronts_0backs_generic_back(self):
        xml = ET.Element("order")

        fronts = ET.SubElement(xml, "fronts")
        fronts.append(self.xml_sol_ring())
        fronts.append(self.xml_black_lotus())

        ET.SubElement(xml, "cardback").text = "1LrVx2978_dkj"

        return self.make_filelike(xml)


    def xml_empty(self):
        return self.make_filelike(ET.Element(""))


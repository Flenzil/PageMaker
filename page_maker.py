import os
import glob
from PIL import Image
import xml.etree.ElementTree as ET

import params as p


class Page:
    def __init__(self, card_width):
        self.card_width = card_width
        self.card_height = int(p.card_ratio * card_width)

        self.page_width = int(p.card_to_page_width_ratio * card_width)
        self.page_height = int(p.page_ratio * self.page_width)

        self.margin_w = int(p.margin_w_ratio * self.page_width)
        self.margin_top = int(p.margin_top_ratio * self.page_height)

        self.clear_page()

    def resize_image(self, image):
        return image.resize((CARD_WIDTH, int(CARD_WIDTH * p.card_ratio)))

    def crop_image(self, image):
        border_crop_w = 0.049
        border_crop_h = 0.037
        left = int(border_crop_w * self.card_width)
        right = self.card_width - int(border_crop_w * self.card_width)
        upper = int(border_crop_h * self.card_height)
        lower = self.card_height - int(border_crop_h * self.card_height)
        return self.resize_image(image.crop((left, upper, right, lower)))


    def add_image_to_page(self, image):
        image = self.resize_image(image)
        image = self.crop_image(image)
        x = self.margin_w + self.current_col * (self.card_width + p.spacing)
        y = self.margin_top + self.current_row * (self.card_height + p.spacing)
        self.page.paste(image, (x, y))
        self.is_empty = False
        self.current_col += 1

        if self.current_col >= p.columns:
            self.current_col = 0
            self.current_row += 1

        if self.current_row >= p.rows:
            self.is_full = True

    def save_page(self, filename):
        self.page.save(filename)

    def clear_page(self):
        self.page = Image.new(
            "RGBA", (self.page_width, self.page_height), (255, 255, 255, 255)
        )
        self.is_empty = True
        self.is_full = False
        self.has_back = False
        self.current_row = 0
        self.current_col = 0


CARD_WIDTH = 3264
IMAGE_PATH = "./images/"
PAGE_PATH = "./pages/"


def main():
    clear_pages_folder()
    create_pages()

def clear_pages_folder():
    pages = glob.glob(PAGE_PATH + "*")
    for i in pages:
        os.remove(i)

def get_card_info():
    card_backs = []    
    with open("cards.xml") as f:
        back_info = ET.parse(f).getroot().find("backs")
        if back_info is not None:
            card_backs.append(back_info)
    return card_backs

# Place card images in a page for printing. Page ratios are set so that
# printing onto a a4 page will result in realistic size cards.
def create_pages():
    page = Page(CARD_WIDTH)
    page_back = Page(CARD_WIDTH)

    page_count = 0

    with open("cards.xml") as f:
        root = ET.parse(f).getroot()
        cards = root.find("fronts")
        backs = root.find("backs")
    
    if cards is None:
        raise Exception("No cards found.")

    for card in cards:
        check_xml(card)

        if backs is not None:
            card_back = get_card_back(card, backs)
        else:
            card_back = None

        for _ in card.find("slots").text.split(","):
            add_card(card, card_back, page, page_back)
            if page.is_full:
                page_count += 1
                save_pages(page, page_back, page_count)

    if not page.is_empty:
        save_pages(page, page_back, page_count + 1)

def check_xml(card):
    if card.find("slots") is None:
        raise Exception("Malformed xml file: \"slots\" element missing.")

def get_card_back(card, backs):
    for back in backs:
        card_slot = card.find("slots")
        back_slot = back.find("slots")
        if card_slot is not None and back_slot is not None:
            if card_slot.text == back_slot.text:
                return back


def save_pages(page, back, name):
    page.save_page(PAGE_PATH + f"/{name}.png")

    if page.has_back:
        back.save_page(PAGE_PATH + f"/{name}_back.png")

    back.clear_page()
    page.clear_page()


# Add card to page, also adds the backside of the card to a seperate
# page if applicable, for double sided cards for example.
def add_card(card, card_back, page, page_back):

    card_image = find_card_image(card)
    if card_image is None:
        raise Exception(f"Image for \"{card.find('query').text}\" not found")

    if card_back is not None:
        back_image = find_card_image(card_back)
        if back_image is None:
            raise Exception(f"Image for \"{card_back.find('query').text}\" not found")

    if card_back is None:
        image = Image.open(card_image)
        page.add_image_to_page(image)
    else:
        image = Image.open(card_image)
        image_back = Image.open(back_image)

        page_back.current_row = page.current_row
        page_back.current_col = p.columns - 1 - page.current_col

        page.add_image_to_page(image)
        page_back.add_image_to_page(image_back)

        page.has_back = True

def find_card_image(card):
    for card_image in os.listdir(IMAGE_PATH):
        if "Zone.Identifier" in card_image:
            continue
        if card.find("id").text in card_image:
            return IMAGE_PATH + card_image


if __name__ == "__main__":
    main()

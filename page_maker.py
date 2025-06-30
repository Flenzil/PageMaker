import os
import glob
import argparse
from PIL import Image, ImageEnhance
import xml.etree.ElementTree as ET

import params as p

IMAGE_PATH = "./images/"
PAGE_PATH = "./pages/"
XML_PATH = "./xml/"


class Page:
    def __init__(self, args):
        self.card_width = p.card_widths[args.quality]
        self.card_height = int(p.card_ratio * self.card_width)

        self.spacing = convert_mm_to_pixels(self.card_width, args.spacing)

        self.card_bleed_w = convert_mm_to_pixels(self.card_width, args.bleed)
        self.card_bleed_h = int(self.card_bleed_w)

        self.crop_w = convert_mm_to_pixels(self.card_width, args.crop_width)
        self.crop_h = convert_mm_to_pixels(self.card_width, args.crop_height)

        self.crop_mark_size = convert_mm_to_pixels(self.card_width, args.crop_mark_size)

        self.page_width = convert_mm_to_pixels(
            self.card_width, p.page_widths[args.page_size]
        )
        self.page_height = int(p.page_ratio * self.page_width)

        self.margin_w = int(
            0.5
            * (
                self.page_width
                - p.columns * self.card_width
                - (p.columns - 1) * self.spacing
            )
        )

        self.margin_top = int(
            0.5
            * (
                self.page_height
                - p.rows * self.card_height
                - (p.rows - 1) * self.spacing
            )
        )

        self.clear_page()

    def resize_image(self, image, bleed):
        if bleed:
            return image.resize(
                (
                    self.card_width + 2 * self.card_bleed_w,
                    self.card_height + 2 * self.card_bleed_h,
                )
            )
        else:
            return image.resize((self.card_width, self.card_height))

    def crop_image(self, image, crop):
        if crop:
            border_crop_w = self.crop_w
            border_crop_h = self.crop_h
        else:
            border_crop_w = 0
            border_crop_h = 0

        left = border_crop_w
        right = self.card_width - border_crop_w
        upper = border_crop_h
        lower = self.card_height - border_crop_h

        return self.resize_image(image.crop((left, upper, right, lower)), False)

    def colour_correct_image(self, image, colour_shift):
        if colour_shift == (0, 0, 0):
            return
        img_data = image.getdata()

        img_cc = []
        for pixel in img_data:
            img_cc.append(
                (
                    pixel[0] + colour_shift[0],
                    pixel[1] + colour_shift[1],
                    pixel[2] + colour_shift[2],
                )
            )
        image.putdata(img_cc)

    def add_bleed(self, image):
        border = Image.new(
            mode="RGB",
            size=(
                self.card_width + 2 * self.card_bleed_w,
                self.card_height + 2 * self.card_bleed_h,
            ),
            color=(0,0,0),
        )
        border.paste(
            image,
            (self.card_bleed_w, self.card_bleed_h),
        )

        return border

    def add_image_to_page(self, image, crop, bleed=False, add_bleed=False):
        if not add_bleed:
            image = self.resize_image(image, bleed)
        else:
            image = self.resize_image(image, False)

        if add_bleed:
            image = self.add_bleed(image)

        if not bleed:
            image = self.crop_image(image, crop)

        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.1)

        self.colour_correct_image(
            image,
            (
                0,
                0,
                0,
            ),
        )
        if bleed:
            x = (
                self.margin_w
                - p.columns * self.card_bleed_w
                + self.current_col
                * (self.card_width + 2 * self.card_bleed_w + self.spacing)
            )
            y = (
                self.margin_top
                - p.rows * self.card_bleed_h
                + self.current_row
                * (self.card_height + 2 * self.card_bleed_h + self.spacing)
            )
        else:
            x = self.margin_w + self.current_col * (self.card_width + self.spacing)
            y = self.margin_top + self.current_row * (self.card_height + self.spacing)

        self.page.paste(image, (x, y))
        if bleed:
            self.add_crop_marks(x, y)

        self.is_empty = False
        self.current_col += 1

        if self.current_col >= p.columns:
            self.current_col = 0
            self.current_row += 1

        if self.current_row >= p.rows:
            self.is_full = True

    def add_crop_marks(self, x, y):
        x_b = x + self.card_bleed_w
        y_b = y + self.card_bleed_h
        crop_marks = [
            (x_b, y_b),
            (x_b + self.card_width, y_b),
            (x_b, y_b + self.card_height),
            (x_b + self.card_width, y_b + self.card_height),
        ]

        crop_mark_size = max(2, self.crop_mark_size)
        crop_mark_start = -int(crop_mark_size / 2)
        crop_mark_end = int(crop_mark_size / 2)
        outline_width = max(2, int(self.crop_mark_size / 3))

        for crop_mark in crop_marks:
            for i in range(crop_mark_start, crop_mark_end):
                for j in range(crop_mark_start, crop_mark_end):
                    if (
                        i < crop_mark_start + outline_width
                        or j < crop_mark_start + outline_width
                        or i >= crop_mark_end - outline_width
                        or j >= crop_mark_end - outline_width
                    ):
                        pixel_colour = (0, 0, 0)
                    else:
                        pixel_colour = (255, 255, 255)

                    self.page.putpixel(
                        (crop_mark[0] + i, crop_mark[1] + j), pixel_colour
                    )

    def save_page(self, filename):
        self.page.save(filename)

    def clear_page(self):
        self.page = Image.new(
            mode="RGB",
            size=(self.page_width, self.page_height),
            color=(255,255,255)
        )
        self.is_empty = True
        self.is_full = False
        self.has_back = False
        self.current_row = 0
        self.current_col = 0

class Card:
    def __init__(self, card, back=None, instances=1):
        self.card = card
        self.instances = instances

        self.id = self.card.find("id").text
        self.image = self.find_card_images(self.id)
        self.name = self.card.find("name").text.title()

        if back is not None:
            self.back = back
            self.has_back = True
            try:
                self.id_back = self.back.find("id").text
                self.name_back = self.back.find("name").text.title()
            except AttributeError:
                self.id_back = self.back.text
                self.name_back = "Card Back"
            self.image_back = self.find_card_images(self.id_back)
            print(self.id_back)
        else:
            self.back = None
            self.id_back = None
            self.image_back = None
            self.name_back = ""
            self.has_back = False

    def __repr__(self):
        if self.has_back:
            return f"{self.name} // {self.name_back}"
        else:
            return self.name 

    def find_card_images(self, card_id):
        for card_image in os.listdir(IMAGE_PATH):
            if "Zone.Identifier" in card_image:
                continue

            import re

            try:
                id = re.findall(r"\((?=[^\(]*$).*(?=\)\.)", card_image)[-1][1:]
            except IndexError:
                raise Exception(f"{self.name} or {self.name_back} not found!")

            if id == card_id:
                return IMAGE_PATH + card_image



def parse_args():
    parser = argparse.ArgumentParser(description="Page Maker")
    parser.add_argument("-s", "--spacing", type=float, default=p.spacing_default)
    parser.add_argument("-b", "--bleed", type=float, default=p.bleed_default)
    parser.add_argument("-p", "--page-size", default=p.page_size_default)
    parser.add_argument("-ch", "--crop-height", type=float, default=p.crop_h_default)
    parser.add_argument("-cw", "--crop-width", type=float, default=p.crop_w_default)
    parser.add_argument("--card_backs", type=bool, default=p.card_backs_default)

    parser.add_argument(
        "-q", "--quality",
        choices=["low", "medium", "high"],
        default="high"
    )
    parser.add_argument(
        "--crop_mark_size",
        type=float,
        default=p.crop_mark_size_default
    )
    parser.add_argument(
        "--no-aggregate-backs",
        action=argparse.BooleanOptionalAction,
        default=p.aggregate_backs_default,
    )
    return parser.parse_args()


def convert_mm_to_pixels(card_width, mm):
    pixels_per_mm = card_width / 63
    return int(mm * pixels_per_mm)


def convert_pixels_to_mm(card_width, pixels):
    mm_per_pixel = 63 / card_width
    return pixels * mm_per_pixel

# Sometimes mpcfill misses an image download for some reason so this checks
# if all of the images for the cards in the .xml are present. Raises an
# exception with a list of missing cards if any.
def check_all_cards_are_present():
    def card_compare(card_id):
        for image_name in os.listdir(IMAGE_PATH):
            if card_id in image_name:
                return True
        return False

    with open(XML_PATH + "cards.xml") as f:
        root = ET.parse(f).getroot()
        cards = root.find("fronts")

    if cards is None:
        raise Exception("No cards found!")

    not_found = []

    for card in cards:
        card_id = card.find("id")
        card_name = card.find("name")
        if card_id is not None:
            card_id = card_id.text
        else:
            raise Exception("ID missing on some cards!")
        if card_name is not None:
            card_name = card_name.text
        else:
            raise Exception("Name missing on some cards!")

        if not card_compare(card_id):
            not_found.append(card_name)

    if not_found == []:
        print("All cards present!")
    else:
        raise Exception(f"The following cards are missing: {not_found}")


# Remove old pages.
def clear_pages_folder():
    pages = glob.glob(PAGE_PATH + "*")
    for i in pages:
        os.remove(i)


def save_pages(page, back, name):
    page.save_page(PAGE_PATH + f"/{name}.jpg")

    if page.has_back:
        back.save_page(PAGE_PATH + f"/{name}_back.jpg")

    back.clear_page()
    page.clear_page()

# Add card to page, also adds the backside of the card to a seperate
# page if applicable, for double sided cards for example.
def add_card(card, page, page_back):
    print(f"Adding {card.card.find('query').text.title()}")
    if set(card.card.find("id").text) == set("x") or card.card.find("name").text[:2] == "c ":
        crop = False
    else:
        crop = True

    if page.has_back:
        bleed = True
    else:
        bleed = False

    # Non MPCFill double sided cards need bleed added manually
    if bleed == True and crop == False:
        add_bleed = True
    else:
        add_bleed = False

    if card.image is None:
        raise Exception(f'Image for "{card.name}" not found')

    if card.back is not None:
        if card.image_back is None:
            raise Exception(f'Image for "{card.name_back}" not found')

    if card.back is None:
        image = Image.open(card.image)
        page.add_image_to_page(image, crop, bleed=bleed, add_bleed=add_bleed)
    else:
        image = Image.open(card.image)
        image_back = Image.open(card.image_back)

        page_back.current_row = page.current_row
        page_back.current_col = p.columns - 1 - page.current_col

        page.add_image_to_page(image, crop, bleed=bleed, add_bleed=add_bleed)
        page_back.add_image_to_page(image_back, crop, bleed=bleed, add_bleed=add_bleed)

        #page.has_back = True


def create_cards(args):
    with open(XML_PATH + "cards.xml") as f:
        root = ET.parse(f).getroot()
        cards = root.find("fronts")
        backs = root.find("backs")
        generic_card_back = root.find("cardback")

    if cards is None:
        raise Exception("No cards found.")
    if backs is None:
        backs = []

    card_objs = []

    slots_back_map = [
        (back, set(back.find("slots").text.split(","))) for back in backs
    ]
    for card in cards:
        slots = set(card.find("slots").text.split(","))

        for back, slots_back in slots_back_map:
            if slots & slots_back:
                card_objs.append(Card(card, back=back, instances=len(slots)))
                break
            if args.card_backs:
                card_objs.append(Card(card, back=generic_card_back, instances=len(slots)))
        else:
            card_objs.append(Card(card, instances=len(slots)))

    if args.no_aggregate_backs:
        return card_objs
    else:
        return sorted(card_objs, key=lambda x: x.has_back)


def batch_cards(cards, page):
    batch = []
    i = 0
    for card in cards:
        for _ in range(card.instances):
            batch.append(card)
            if card.has_back:
                page.has_back = True
            if i >= 8:
                return batch
            i += 1
    return batch

def add_card_to_page(batch, cards, page, page_back):
    for card in batch:
        add_card(card, page, page_back)
        card.instances -= 1

        if card.instances <= 0:
            cards.remove(card)


def create_pages(args):
    page = Page(args)
    page_back = Page(args)

    page_count = 1

    cards = create_cards(args)
    batch = batch_cards(cards, page)

    while len(cards) > 0:
        if page.is_empty:
            print(f"Creating page {page_count}...")
        add_card_to_page(batch, cards, page, page_back)

        if page.is_full:
            print()
            print(f"Saving page {page_count}... ", end="", flush=True)
            save_pages(page, page_back, page_count)
            print("Saved!")
            print()

            page_count += 1
        
        batch = batch_cards(cards, page)

    if not page.is_empty:
        print(f"Saving page {page_count}... ", end="")
        save_pages(page, page_back, page_count)
        print("Saved!")


def main():
    check_all_cards_are_present()
    clear_pages_folder()
    create_pages(parse_args())


if __name__ == "__main__":
    main()

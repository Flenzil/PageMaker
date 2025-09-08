from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
IMAGE_PATH = Path(ROOT / "data/images")
CUSTOM_IMAGE_PATH = Path(ROOT / "data/custom images")
PAGE_PATH = Path(ROOT / "pages")
XML_PATH = Path(ROOT / "data/xml")

# Resolution
card_width_high = 3000
card_width_medium = int(card_width_high / 2)
card_width_low = int(card_width_high / 4)


# Parameters in millimetres
card_width_in_mm = 63
spacing_default = 0.1
bleed_default = 3.175
margin_x_min = 1
margin_y_min = 1
crop_mark_size_default = 0.75
crop_mark_border_size_default = 0.2

mpcfill_bleed = 3.175 # MPCFill images have a 1/8" = 3.175mm bleed on all sides.

page_size_default = "a4"
brightness_adjust_default = 1.0

card_widths = {
    "low": card_width_low,
    "medium": card_width_medium,
    "high": card_width_high,
}

# Add the generic magic back to each card
card_backs_default = False

#Collect cards with backs together, to minimise amount of pages that have back sides.
no_aggregate_backs_default = False

#Never add bleed
no_bleed_default = False

#Always add bleed
always_bleed_default = False

save_as_pdf_default = False

# Dimension Ratios
card_ratio = 1.3968
page_ratio = 1.4142135623730  # sqrt(2)

MAX_PAGE_SIZE_NUMBER = 7
MIN_PAGE_SIZE_NUMBER = 0

MAX_DOWNLOAD_RETRIES = 3


try:
    from params_local import * #NOQA
except ImportError:
    pass

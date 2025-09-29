from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
IMAGE_PATH = Path(ROOT / "data/images")
CUSTOM_IMAGE_PATH = Path(ROOT / "data/custom images")
PAGE_PATH = Path(ROOT / "pages")
XML_PATH = Path(ROOT / "data/xml")

# Resolution of cards in pixels
card_width_high = 3000
card_width_medium = int(card_width_high / 2)
card_width_low = int(card_width_high / 4)

quality_default = 'high'

card_widths = {
    "low": card_width_low,
    "medium": card_width_medium,
    "high": card_width_high,
}

# Parameters in millimetres
card_width_in_mm = 63
spacing_default = 0.15
bleed_default = 3.175
margin_x_min = 1
margin_y_min = 1
crop_mark_size_default = 0.75
crop_mark_border_size_default = 0.2

mpcfill_bleed = 3.175 # MPCFill images have a 1/8" = 3.175mm bleed on all sides.


# Limits on the page size number i.e the '4' in A4.
MAX_PAGE_SIZE_NUMBER = 7
MIN_PAGE_SIZE_NUMBER = 0
page_size_default = "a4"
page_size_choices = [f'{letter}{number}' for letter in ['a','b','c'] for number in range(MIN_PAGE_SIZE_NUMBER, MAX_PAGE_SIZE_NUMBER)]


# Factor by which images are brightened
brightness_adjust_default = 1.0

# Add the generic magic back to each card
card_backs_default = False

#Collect cards with backs together, to minimise amount of pages that have back sides.
no_aggregate_backs_default = False

#Never add bleed
no_bleed_default = False

#Always add bleed
always_bleed_default = False

# Aggregate images into a single pdf
save_as_pdf_default = False
collate_back_pages_default = False

# Dimension Ratios
card_ratio = 1.3968
page_ratio = 1.4142135623730  # sqrt(2)


# Download paramaters
MAX_DOWNLOAD_RETRIES = 3
MAX_BACKOFF = 30
backoff_mult = 1.5
download_chunk_size = 1024 * 256
max_simultaneous_downloads = 10


# Amount of background workers for saving pages concurrently
number_of_saving_workers = 4

try:
    from src.params_local import * #NOQA
except ImportError:
    pass

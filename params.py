# Resolution
card_width_high = 3326
card_width_medium = int(card_width_high / 2)
card_width_low = int(card_width_high / 4)


# Parameters in millimetres
card_width_in_mm = 63
spacing_default = 0.1
bleed_default = 3.175 # MPCFill images have a 1/8" = 3.175mm bleed on all sides.
crop_w_default = 3.175
crop_h_default = 3.175
crop_mark_size_default = 0.75
crop_mark_border_size_default = 0.2

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

# Dimension Ratios
card_ratio = 1.3968
page_ratio = 1.4142135623730  # sqrt(2)

MAX_PAGE_SIZE_NUMBER = 7
MIN_PAGE_SIZE_NUMBER = 0


def get_page_widths(page_size):
    """Calculates the width of a given A, B, or C series paper size.

    All A, B and C series paper share the same height-width ratio: sqrt(2).
    This function computes the width of any page size by scaling from known
    base width (A4, B4, C4 to minimise computation for most common types).

    Args:
        page_size (str): Page size in form of A4, C5 etc.
    """

    page_widths = {"a": 210, "b": 250, "c": 229}
    series = page_size[0].lower()
    step_from_base = 4 - int(page_size[1]) #A4 = 0, B3 = 1, C5 = -1 etc.
    return int(page_widths[series] * pow(pow(2, 0.5), step_from_base))

try:
    from params_local import * #NOQA
except ImportError:
    pass

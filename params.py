# Resolution
card_width_high = 3326
card_width_medium = int(card_width_high / 2)
card_width_low = int(card_width_high / 4)


# Parameters in millimetres
spacing_default = 0.1
bleed_default = 3.175
crop_mark_size_default = 0.75
crop_mark_border_size_default = 0.2
page_size_default = "a4"

# MPCFill say that their images have a 1/8" = 3.175mm bleed on all sides,
# however in my measuring I've found that 2.41mm is much more accurate.
crop_w_default = 2.41
crop_h_default = 2.41

page_widths = {"a4": 210}
columns = {"a4": 3}
rows = {"a4": 3}

card_widths = {
    "low": card_width_low,
    "medium": card_width_medium,
    "high": card_width_high,
}

# Add the generic magic back to each card
card_backs_default = False
no_aggregate_backs_default = False

# Dimension Ratios
card_ratio = 1.3968
page_ratio = 1.4142135623730  # sqrt(2)

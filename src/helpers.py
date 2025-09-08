import src.params as params
from pathlib import Path

def get_page_widths(page_size: str) -> int:
    """Calculates the width of a given A, B, or C series paper size.

    All A, B and C series paper share the same height-width ratio: sqrt(2).
    This function computes the width of any page size by scaling from known
    base width (A4, B4, C4 to minimise computation for most common types).

    Args:
        page_size (str): Page size in form of A4, C5 etc.
    Returns:
        (int): page width in mm
    """

    page_widths = {"a": 210, "b": 250, "c": 229}
    series = page_size[0].lower()
    step_from_base = 4 - int(page_size[1]) #A4 = 0, B3 = 1, C5 = -1 etc.
    return int(page_widths[series] * pow(pow(2, 0.5), step_from_base))

def convert_mm_to_pixels(card_width: float, mm: float) -> int:
    """Converts from millimetres to pixels on the page. The card width is a known
    quantity: mtg cards are 63mm wide. So we use it for conversion.
    """
    pixels_per_mm = card_width / params.card_width_in_mm
    return int(mm * pixels_per_mm)


def convert_pixels_to_mm(card_width: float, pixels: int) -> float:
    """Converts from pixels on the page to millimetres. The card width is a known
    quantity: mtg cards are 63mm wide. So we use it for conversion.
    """
    mm_per_pixel = params.card_width_in_mm / card_width
    return pixels * mm_per_pixel

def get_all_images_from_folder(path: Path) -> list[str]:
    images = []
    image_exts = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg']
    for image in path.glob("*"):
        if image.suffix not in image_exts:
            continue
        images.append(str(image.name))
    return images

def ceiling_divide(a, b):
    return int(-(a // -b))

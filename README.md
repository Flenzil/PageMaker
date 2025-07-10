# PageMaker

PageMaker is a Python script that formats MTG cards into printable pages. Designed to work with MPCFill, it supports double sided card layouts. Very flexible in page layouts and page sizes.

## Features
- Automatically download card images from `.xml` data.
- Automatically arranges cards into a grid on standard paper sizes (e.g A4, B5, C3 etc.)
- Supports double sided cards and can optionally include generic back on every card.
- Outputs pages into .jpg image files.
- Flexible page layout; allows you to control the spacing, margins, bleed and image brightness.

## Requirements
- Python 3.7+
- Pillow 10.40+

Install dependencies with:
```
pip install -r requirements.txt
```

## Usage
1. Download card images and `.xml` from MPCFIll.
2. Put all card images (fronts and backs) into `/images/` and the XML file (named `cards.xml`) into `/xml/`.
3. Run the script:
```
python3 page_maker.py
```


Developers can create a `params_local.py` in the root folder to override parameters in `params.py` without overwriting the original.

## Optional Arguments
|Long Argument|Short Argument|Description|Default|
|:-----------:|:------------:|:---------:|:-----:|
|--quality    |    -q        |Output image quality: `high`, `medium`, `low`.| `high` |
|--spacing    |-s            |Horizonal and vertical space between cards on the page.| `0.1mm` |
|--spacing-x    |-sx            |Horizonal space between cards on the page. Uses --spacing if not supplied.| `None` |
|--spacing-y    |-sy           |Vertical space between cards on the page. Uses --spacing if not supplied.| `None` |
|--bleed    |-b            | Bleed around each card. MPCFill cards have 1/8" (3.175mm) of bleed. | `3.175mm` |
|--bleed-x    |-bx            |Bleed in the x direction. Uses --bleed if not supplied| `None` |
|--bleed-y    |-by            |Bleed in the y direction. Uses -bleed if not supplied| `None` |
|--page-size    |-p            |Page type to use. Only `"a4"` is currently supported.| `"a4"` |
|--card-backs    |            |Use a generic card back for cards without a back side.| `False` |
|--brightness-adjust    |            |Brightness multiplier to apply to each card image.| `1.0` |
|--crop-mark-size    |            |Size of crop marks shown when bleed is retained. Useful for cutting alignment.| `0.75mm` |
|--no-bleed    |            |Never add bleed to any card| `False` |
|--always-bleed   |            |Always add bleed to every card| `False` |


Example:

```
python3 page_maker.py -q medium -bx 1 --card-backs
```

## Installation
Git:
```
git clone https://github.com/Flenzil/PageMaker
```


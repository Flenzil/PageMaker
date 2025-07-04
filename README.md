# PageMaker

PageMaker is a Python script that formats cards into printable pages. Designed to work with MPCFill,
it supports front-and-back card layouts

## Features
- Automatically arranges cards into a grid on standard paper sizes (e.g A4)
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


## Optional Arguments
|Long Argument|Short Argument|Description|Default|
|:-----------:|:------------:|:---------:|:-----:|
|--quality    |    -q        |Output image quality: `high`, `medium`, `low`.| `high` |
|--spacing    |-s            |Horizonal and vertical space between cards on the page.| `0.1mm` |
|--spacing-x    |-sx            |Horizonal space between cards on the page. Uses spacing if not supplied.| `None` |
|--spacing-y    |-sy           |Vertical space between cards on the page. Uses spacing if not supplied.| `None` |
|--bleed    |-b            | Bleed around each card. MPCFill cards have 1/8" (3.175mm) of bleed. | `3.175mm` |
|--page-size    |-p            |Page type to use. Only `"a4"` is currently supported.| `"a4"` |
|--crop-height    |-ch            |Amount to crop from the top and bottom of each card.| `3.175mm` |
|--crop-width    |-cw            |Amount to crop from the left and right of each card.| `3.175mm` |
|--card-backs    |            |Use a generic card back for cards without a back side.| `False` |
|--brightness-adjust    |            |Brightness multiplier to apply to each card image.| `1.0` |
|--crop-mark-size    |            |Size of crop marks shown when bleed is retained. Useful for cutting alignment.| `0.75mm` |


Example:

```
python3 page_maker.py -q medium -sx 0.5 --card-backs
```

## Installation
Git:
```
git clone https://github.com/Flenzil/PageMaker
```


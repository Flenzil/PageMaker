# PageMaker

PageMaker is a Python script that formats MTG cards into printable pages. Designed to work with MPCFill, it supports double sided card layouts. Very flexible in page layouts and page sizes.

## Features
- Automatically download card images from `.xml` data.
- Automatically arranges cards into a grid on standard paper sizes (e.g A4, B5, C3 etc.)
- Supports double sided cards and can optionally include generic back on every card.
- Outputs pages into .jpg image files.
- Flexible page layout; allows you to control the spacing, margins, bleed and image brightness.

## Requirements
- `python 3.4+`
- `pillow 10.4.0`
- `requests 2.32.4`

Install dependencies with:
```
pip install -r requirements.txt
```

## Usage
1. Download `cards.xml` from your MPCFIll project and put it into `data/xml`.
2. Navigate to the `page_maker/` folder
3. Run the script:
```
python3 src/page_maker.py
```

Optionally put any additional card images (fronts and backs) into `data/images/`. Additional images need to be added to `cards.xml` for the script to be aware of them. Save the additional
images with the naming structure `name (id)` then add that id to `cards.xml`, use one of the other cards as a template for what the new entry should look like. Make sure to give it a 
unique slot number(s) too. If this card does not have any bleed around it, make the id number only out of x's (e.g `Sol Ring (xxxx).png`, any number of x's will work, just make sure no 
two cards have the same amount.) so that the programme knows not to crop it down. Yes this is very manual and tedious and yes I hope to make this far simpler.

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
python3 src/page_maker.py -q medium -bx 1 --card-backs
```

## Installation
Git:
```
git clone https://github.com/Flenzil/PageMaker
```


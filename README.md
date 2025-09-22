# PageMaker

PageMaker is a Python script that formats MTG cards into printable pages. Designed to work with MPCFill, it supports double sided card layouts. Very flexible in page layouts and page sizes.

## Features
- Automatically download card images from `.xml` data.
- Automatically arranges cards into a grid on standard paper sizes (e.g `A4`, `B5`, `C3` etc.)
- Supports double sided cards and can optionally include generic back on every card.
- Limited support for cards from other sources - just pop them into the custom_images folder.
- Outputs pages into .jpg image files or optionally as a single `.pdf` (currently only available for `A4` page size due to size limitations on the `.pdf` format).
- Flexible page layout; allows you to control the spacing, margins, bleed and image brightness.

## Requirements
- `python 3.4+`
- `pillow-SIMD 9.5.0+` 
- `aiohttp 3.12.14+`
- `aiofiles 24.1.0+`
- `questionary 2.1.0+`
- `rich 14.0.0+`

Install dependencies with:
```
pip install -r requirements.txt
```

## Usage
1. Download `cards.xml` from your MPCFIll project and put it into `data/xml`.
2. Put any extra card images you'd like added to the pages into the `data/custom_images` folder.
3. Navigate to the `PageMaker/` folder in the command line
4. Run the script:

Linux:
```
python3 -m src.main
```

Windows:
```
python -m src.main
```


The script will first check if the `data/images` folder has any cards left over from a previous 
run that are not in the current `cards.xml` and will remove them. 

If there any images in `data/custom_images`, a prompt will appear asking if you want to add the 
images found there to the project as front side or back side cards. If back side is chosen, a prompt
will then appear asking which card will the be the front side of that card, producing a list of 
all cards found in `cards.xml` as well as other images inside `data/custom_images`. You can
even replace the back sides of cards that already have a back in `cards.xml`.

Then it will download any missing images of cards in `cards.xml` into `data/images`, creating the 
folder if necessary.

Developers can create a `params_local.py` in the root folder to override parameters in `params.py` without overwriting the original.

## Optional Arguments
|Long Argument|Short Argument|Description|Default|
|:-----------:|:------------:|:---------:|:-----:|
|--quality    |    -q        |Output image quality: `high`, `medium`, `low`.| `high` |
|--spacing    |-s            |Horizonal and vertical space between cards on the page.| `0.15mm` |
|--spacing-x    |-sx            |Horizonal space between cards on the page. Uses --spacing if not supplied.| `None` |
|--spacing-y    |-sy           |Vertical space between cards on the page. Uses --spacing if not supplied.| `None` |
|--bleed    |-b            | Bleed around each card. MPCFill cards have 1/8" (3.175mm) of bleed. | `3.175mm` |
|--bleed-x    |-bx            |Bleed in the x direction. Uses --bleed if not supplied| `None` |
|--bleed-y    |-by            |Bleed in the y direction. Uses --bleed if not supplied| `None` |
|--page-size    |-p            |ISO 216 paper size to use. Supports `A`, `B` and `C` paper from `A0` - `A7`| `"a4"` |
|--card-backs    |            |Use a generic card back for cards without a back side.| `False` |
|--brightness-adjust    |            |Brightness multiplier to apply to each card image.| `1.0` |
|--crop-mark-size    |            |Size of crop marks shown when bleed is retained. Useful for cutting alignment.| `0.75mm` |
|--no-bleed    |            |Never add bleed to any card| `False` |
|--always-bleed   |            |Always add bleed to every card| `False` |
|--save-as-pdf   |            |Save images as a single `.pdf` file rather than seperate `.jpg` images| `False` |


Example:

```
python3 src/page_maker.py -q medium -bx 1 --card-backs
```

## Installation
Git:
```
git clone https://github.com/Flenzil/PageMaker
```


## Future Additions
- UI

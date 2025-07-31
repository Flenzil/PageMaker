# PageMaker

PageMaker is a Python script that formats MTG cards into printable pages. Designed to work with MPCFill, it supports double sided card layouts. Very flexible in page layouts and page sizes.

## Features
- Automatically download card images from `.xml` data.
- Automatically arranges cards into a grid on standard paper sizes (e.g `A4`, `B5`, `C3` etc.)
- Supports double sided cards and can optionally include generic back on every card.
- Limited support for cards from other sources - just pop them into the images folder.
- Outputs pages into .jpg image files or optionally as a single `.pdf` (currently only available for `A4` page size due to size limitations on the `.pdf` format).
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
2. Put any extra card images you'd like added to the pages into the `data/images` folder.
3. Navigate to the `page_maker/` folder
4. Run the script:
```
python3 src/page_maker.py
```

The script will download images from `cards.xml` into `data/images`. It will also add any cards that don't have ids (i.e the cards you added to `data/images`)
to `cards.xml` and will add an id number to their image name, to match the MPCFill template. The id will be made only of `x`. This is to signal to the
code to not crop any bleed from the card as it is assumed that any cards you add don't have bleed.

If you later remove any cards from `cards.xml`, or indeed download an entirely new one, you will be prompted as to whether you would like to delete the 
image(s). This is to stop a big pile up of images over multiple runs but still allowing multiple runs without having to re-download the images if you want to 
mess around with the parameters.

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
- Back and front support for non MPCFill cards.
- UI

import argparse
import sys
import re
from dataclasses import dataclass
import src.params as params
import src.helpers as helpers
from typing import Any, Mapping

@dataclass
class CLIArgs:
    '''Data class for CLI arguments, can contain any number of keyword arguments'''
    kwargs: Mapping[Any, Any]

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __getattr__(self, name):
        return self.kwargs[name]


class CLIArgsManager:
    '''
    Parse, validate, and normalize command-line arguments.

    This class wraps `argparse` to define supported CLI options, ensures that
    provided arguments conform to expected constraints (e.g., valid page size,
    non-negative bleed), and converts them into pixel-based values suitable for
    downstream use.
    '''
    def __init__(self, argv):
        self.argv = argv

        if self.argv is None:
            self.cli_args = self.create_cli_args().parse_args()
        else:
            self.cli_args = self.create_cli_args().parse_args(self.argv)

        self.validate_cli_args()

        self.card_width = params.card_widths[self.cli_args.quality]

    def create_cli_args(self) -> argparse.ArgumentParser:
        """Create and handle command-line arguments."""
        parser = argparse.ArgumentParser(description="Page Maker")
        parser.add_argument("-q", "--quality", choices=["low", "medium", "high"], default=params.quality_default, help='Card image quality')
        parser.add_argument("-s", "--spacing", type=float, default=params.spacing_default, help='Spacing between cards in mm')
        parser.add_argument("-sx", "--spacing-x", type=float, default=None, help='Horizontal spacing between cards in mm')
        parser.add_argument("-sy", "--spacing-y", type=float, default=None, help='Vertical spacing between cards in mm')
        parser.add_argument("-b", "--bleed", type=float, default=params.bleed_default, help='Desired amount of bleed around card images')
        parser.add_argument("-bx", "--bleed-x", type=float, default=None, help='Desired amount of horizontal bleed around card images')
        parser.add_argument("-by", "--bleed-y", type=float, default=None, help='Desired amount of veritcal bleed around card images')
        parser.add_argument("-p", "--page-size", choices= params.page_size_choices, default=params.page_size_default, help='Page size e.g A4, B3, C2 etc.')
        parser.add_argument("--brightness-adjust", type=float, default=params.brightness_adjust_default, help='Optional brightness adjustment for pages')
        parser.add_argument("--use-generic-card-backs", action="store_true", default=params.card_backs_default, help='Use generic card back images')
        parser.add_argument("--always-use-bleed", action="store_true", default=params.always_bleed_default, help='Apply bleed to every card image')
        parser.add_argument("--never-use-bleed", action="store_true", default=params.no_bleed_default, help='Crop bleed from every card image')
        parser.add_argument("--save-as-pdf", action="store_true", default=params.save_as_pdf_default, help='Additionally save pages as a single .pdf')
        parser.add_argument("--collate-back-pages", action="store_true", default=params.collate_back_pages_default, help='Place back pages after its corrosponding front page')
        parser.add_argument("--crop-mark-size", type=float, default=params.crop_mark_size_default, help='Size of crop marks on cards with bleed')

        # Set values for frontend sliders
        parser.set_defaults(spacing_min=0, spacing_max=2, spacing_step=0.1, spacing_unit='mm',
                            bleed_min=0, bleed_max=5, bleed_step=0.005, bleed_unit='mm',
                            brightness_adjust_min=0, brightness_adjust_max=2, brightness_adjust_step=0.05, brightness_adjust_unit='',
                            crop_mark_size_min=0, crop_mark_size_max=2, crop_mark_size_step=0.05, crop_mark_size_unit='mm',
                            )
        return parser

    def validate_cli_args(self):
        if not re.match(r"^[abc]{1}\d{1}$", self.cli_args.page_size.lower()):
            print(f"{self.cli_args.page_size} page size not supported. Use A4, B3, C5 etc.")
            sys.exit(1)

        page_size_number = int(self.cli_args.page_size[1:])
        if (page_size_number > params.MAX_PAGE_SIZE_NUMBER
            or page_size_number < params.MIN_PAGE_SIZE_NUMBER):
            print("Page size too small! Try a larger page.")
            sys.exit(1)

        if self.cli_args.always_use_bleed and self.cli_args.never_use_bleed:
            print("--always-bleed and --no-bleed are mutually exclusive")
            sys.exit(1)

        if (self.cli_args.bleed < 0 or
            (self.cli_args.bleed_x is not None and self.cli_args.bleed_x < 0) or 
            (self.cli_args.bleed_y is not None and self.cli_args.bleed_y < 0)):
            print("Bleed cannot be negative.")
            sys.exit(1)

        if (self.cli_args.never_use_bleed and 
            (self.cli_args.bleed != params.bleed_default or
            self.cli_args.bleed_x is not None or 
            self.cli_args.bleed_y is not None)):
            print("#######################################################################################")
            print("WARNING: Bleed is specified but --no-bleed is set to True. Bleed value will be ignored.")
            print("#######################################################################################")

        if self.cli_args.always_use_bleed and self.cli_args.bleed == 0:
            print("#######################################################################################")
            print("--always-bleed is True but bleed is set to 0. Consider using --no_bleed")
            print("#######################################################################################")

        if self.cli_args.page_size.lower() != "a4" and self.cli_args.save_as_pdf:
            print("Saving as a .pdf is only available for A4. This is due to size restrictions on the .pdf format.")
            sys.exit(1)

    def get_cli_args(self) -> CLIArgs:
        '''Create container for cli arguments'''
        args = CLIArgs(
            card_width=self.card_width,
            card_height=self.get_card_height(),
            spacing_x=self.get_spacing_x(),
            spacing_y=self.get_spacing_y(),
            card_bleed_x=self.get_card_bleed_x(),
            card_bleed_y=self.get_card_bleed_y(),
            mpcfill_bleed=self.get_mpcfill_bleed(),
            no_bleed=self.get_no_bleed(),
            always_bleed=self.get_always_bleed(),
            card_crop_x=self.get_card_crop_x(),
            card_crop_y=self.get_card_crop_y(),
            crop_mark_size=self.get_crop_mark_size(),
            page_width=self.get_page_width(),
            page_height=self.get_page_height(),
            brightness_adjust=self.get_brightness_adjust(),
            use_generic_card_backs=self.get_use_generic_card_backs(),
            save_as_pdf=self.get_save_as_pdf(),
            collate_back_pages=self.get_collate_back_pages()
        )
        return args

    def get_card_height(self) -> int:
        '''Height of the card in pixels'''
        return int(params.card_ratio * self.card_width)

    def get_page_width(self) -> int:
        '''Width of the page in pixels'''
        page_size = self.cli_args.page_size.lower()
        return helpers.convert_mm_to_pixels(self.card_width, helpers.get_page_widths(page_size))

    def get_page_height(self) -> int:
        '''Height of the page in pixels'''
        return int(params.page_ratio * self.get_page_width())

    def get_spacing_x(self) -> int:
        '''Horizontal spacing between cards in pixels'''
        if self.cli_args.spacing_x is None:
            spacing_x = helpers.convert_mm_to_pixels(self.card_width, self.cli_args.spacing)
        else:
            spacing_x = helpers.convert_mm_to_pixels(self.card_width, self.cli_args.spacing_x)
        return spacing_x

    def get_spacing_y(self) -> int:
        '''Vertical spacing between cards in pixels'''
        if self.cli_args.spacing_y is None:
            spacing_y = helpers.convert_mm_to_pixels(self.card_width, self.cli_args.spacing)
        else:
            spacing_y = helpers.convert_mm_to_pixels(self.card_width, self.cli_args.spacing_y)
        return spacing_y
            
    def get_card_bleed_x(self) -> int:
        '''Desired amount of horizontal bleed in pixels'''
        if self.cli_args.bleed_x is None:
            card_bleed_x = helpers.convert_mm_to_pixels(self.card_width, self.cli_args.bleed)
        else:
            card_bleed_x = helpers.convert_mm_to_pixels(self.card_width, self.cli_args.bleed_x)

        return card_bleed_x

    def get_card_bleed_y(self) -> int:
        '''Desired amount of veritcal bleed in pixels'''
        if self.cli_args.bleed_y is None:
            card_bleed_y = helpers.convert_mm_to_pixels(self.card_width, self.cli_args.bleed)
        else:
            card_bleed_y = helpers.convert_mm_to_pixels(self.card_width, self.cli_args.bleed_y)
        return card_bleed_y

    def get_mpcfill_bleed(self) -> int:
        '''Amount of bleed added by MPCFill in pixels'''
        return helpers.convert_mm_to_pixels(self.card_width, params.mpcfill_bleed)

    def get_no_bleed(self) -> bool:
        '''True if cards should have never have any bleed'''
        return self.cli_args.never_use_bleed

    def get_always_bleed(self) -> bool:
        '''True if all cards should have bleed'''
        return self.cli_args.always_use_bleed

    def get_card_crop_x(self) -> int:
        '''Amount of horizontal cropping needed in pixels'''
        return self.get_mpcfill_bleed() - self.get_card_bleed_x()

    def get_card_crop_y(self) -> int:
        '''Amount of vertical cropping needed in pixels'''
        return  self.get_mpcfill_bleed() - self.get_card_bleed_y()

    def get_crop_mark_size(self) -> int:
        '''Width/height of square crop marks put on cards with bleed to help cutting in pixels'''
        return helpers.convert_mm_to_pixels(self.card_width, self.cli_args.crop_mark_size)

    def get_brightness_adjust(self) -> float:
        '''Amount of brightening applied to cards, helps when some printers print dark.'''
        return self.cli_args.brightness_adjust

    def get_use_generic_card_backs(self) -> bool:
        '''True if every card without a back already will use a generic image for the back side'''
        return self.cli_args.use_generic_card_backs

    def get_save_as_pdf(self) -> bool:
        '''True if the images should be aggregated into a single .pdf file'''
        return self.cli_args.save_as_pdf
    
    def get_collate_back_pages(self) -> bool:
        '''True if the back pages should be placed after its corrosponding front page'''
        return self.cli_args.collate_back_pages


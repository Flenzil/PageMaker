from PIL import Image, ImageDraw
from PIL.Image import Image as PILImageType
from src.card import DoubleSidedCard
from pathlib import Path

import src.params as params
from src.cli_args_manager import CLIArgs

class Page():
    '''A virtual page onto which the card images are placed

    This represents a single page containing cards and is used to
    manipulate the images (cropping, resizing etc.) and ensuring 
    that the cards print out to the right size. 

    Attributes:
        args (CLIArgs): Object containing all command-line arguments
        has_back (bool): True is this page has a back side
        keep_bleed (bool): True if the bleed on cards is not to be cropped off
    '''
    def __init__(self, args: CLIArgs, has_back: bool=False) -> None:
        '''Initialise the page.
            
        Args:
            cli_args (CLIArgs): Data class containing command-line arguments from user.
            is_back (bool): True if this page contains the back side of cards.
        '''

        self.has_back = has_back
        self.args = args

        if (self.has_back and not self.args.no_bleed) or self.args.always_bleed:
            self.keep_bleed = True
        else:
            self.keep_bleed = False

        #Reset page
        self.clear_page()


    def calculate_rows_and_cols(self) -> tuple[int, int]:
        '''Find the maximum number of rows and columns this page can contain and
        then calculate the margins
        '''
        #Number of rows and columns, set by the page size e.g a4 pages can hold 
        #3x3 mtg cards.
        if (not self.args.no_bleed and self.has_back) or self.args.always_bleed:
            columns = self.args.page_width // (self.args.card_width + 2 * self.args.card_bleed_x + self.args.spacing_x)
            rows = self.args.page_height // (self.args.card_height + 2 * self.args.card_bleed_y + self.args.spacing_y)
        else:
            columns = self.args.page_width // (self.args.card_width + self.args.spacing_x)
            rows = self.args.page_height // (self.args.card_height + self.args.spacing_y)

        return columns, rows


    def calculate_margins(self) -> tuple[int, int]:
        '''Margins around edge of page, derived by the negative space left by other
        variables.
        '''
        margin_x = int(
            0.5
            * (
                self.args.page_width
                - self.columns * self.args.card_width
                - (self.columns - 1) * self.args.spacing_x
            )
        )
        margin_x = max(params.margin_x_min, margin_x)

        margin_y = int(
            0.5
            * (
                self.args.page_height
                - self.rows * self.args.card_height
                - (self.rows - 1) * self.args.spacing_y
            )
        )
        margin_y = max(params.margin_y_min, margin_y)

        return margin_x, margin_y


    def clear_page(self) -> None:
        '''Create empty page and reset associated variables'''
        self.page = None
        self.back = None
        self.is_empty = True
        self.is_full = False
        self.columns, self.rows = self.calculate_rows_and_cols()
        self.margin_x, self.margin_y = self.calculate_margins()
        self.current_row = 0
        self.current_col = 0
        self.current_col_back = self.columns - self.current_col - 1



    def add_crop_marks(self, page: PILImageType, x: int, y: int) -> None:
        '''Add visual crop marks to guide cutting when bleed is present.
        
        Draws small squares at each corner of the card using a black border
        with a white interior, ensuring visibility on any background.

        Args:
            x (int): x pixel position of top left corner of card
            y (int): y pixel position of top left corner of card
        '''

        x_b = x + self.args.card_bleed_x
        y_b = y + self.args.card_bleed_y
        crop_marks = [
            (x_b, y_b),
            (x_b + self.args.card_width, y_b),
            (x_b, y_b + self.args.card_height),
            (x_b + self.args.card_width, y_b + self.args.card_height),
        ]

        crop_mark_size = max(2, self.args.crop_mark_size)
        outline_width = max(2, self.args.crop_mark_size // 4)

        draw = ImageDraw.Draw(page)
        ch = crop_mark_size // 2

        for cx, cy in crop_marks:
            box_corners = [cx - ch, cy - ch, cx + ch, cy + ch]
            draw.rectangle(
                box_corners,
                fill='white',
                outline='black',
                width=outline_width
            )

    def adjust_brightness(self, image: PILImageType) -> PILImageType:
        '''Adjust brightness of card image'''
        if self.args.brightness_adjust == 1:
            return image

        #Define look-up table
        lut = [min(255, int(i * self.args.brightness_adjust)) for i in range(256)] * 3
        image = image.point(lut)

        return image


    def paste_position(self, current_col: int) -> tuple[int, int]:
        '''Finds the x and y pixel position on the page to paste the card

        Args:
            current_col (int): Current column on page; different for front and back

        Returns:
            (int): x pixel position to which to paste card image
            (int): y pixel position to which to paste card image
        '''
        if self.keep_bleed:
            x = (
                self.margin_x
                - self.columns * self.args.card_bleed_x
                + current_col
                * (self.args.card_width + 2 * self.args.card_bleed_x + self.args.spacing_x)
            )
            y = (
                self.margin_y
                - self.rows * self.args.card_bleed_y
                + self.current_row
                * (self.args.card_height + 2 * self.args.card_bleed_y + self.args.spacing_y)
            )
        else:
            x = self.margin_x + current_col * (self.args.card_width + self.args.spacing_x)
            y = self.margin_y + self.current_row * (self.args.card_height + self.args.spacing_y)

        return x, y


    def transform_image(self, image: PILImageType, has_bleed: bool) -> PILImageType:
        '''
        Crop and resize image. Some tricks need to be used since the desired order
        of operations is resize -> crop, but Image.transform executes crop -> resize.
        Image.transform is much faster than cropping and resizing independantly.

        Args:
            image (PILImageType): Image of card
            has_bleed (bool): True is the card image has bleed around the card

        Returns:
            (PILImageType): Resized and cropped card image.
        '''
        if has_bleed:
            target_size = (
                    self.args.card_width + 2 * self.args.mpcfill_bleed,
                    self.args.card_height + 2 * self.args.mpcfill_bleed,
                )
        else:
            target_size = (self.args.card_width, self.args.card_height)

        if self.keep_bleed and has_bleed:
            left = self.args.card_crop_x
            right = self.args.card_width + 2 * self.args.mpcfill_bleed - self.args.card_crop_x
            upper = self.args.card_crop_y
            lower = self.args.card_height + 2 * self.args.mpcfill_bleed - self.args.card_crop_y
        elif self.keep_bleed and not has_bleed:
            left = -self.args.card_bleed_x
            right = self.args.card_width + self.args.card_bleed_x
            upper = -self.args.card_bleed_y
            lower = self.args.card_height + self.args.card_bleed_y
        elif not self.keep_bleed and has_bleed:
            left = self.args.mpcfill_bleed
            right = self.args.card_width + self.args.mpcfill_bleed
            upper = self.args.mpcfill_bleed
            lower = self.args.card_height + self.args.mpcfill_bleed
        else:
            left = 0
            right = self.args.card_width
            upper = 0
            lower = self.args.card_height

        # Scale cropping to resized coords
        w_orig, h_orig = image.size

        scale_x = w_orig / target_size[0]
        scale_y = h_orig / target_size[1]

        crop_box = (
            left * scale_x,
            upper * scale_y,
            right * scale_x,
            lower * scale_y
        )

        return image.transform(size=(right - left, lower - upper), method=Image.EXTENT, data=crop_box)


    def adjust_image(self, image: PILImageType, has_bleed: bool) -> PILImageType:
        '''Resize, crop and brighten card image.'''
        image = self.transform_image(image, has_bleed=has_bleed)
        return image


    def paste_image(self, image: PILImageType|None, page: PILImageType, has_bleed: bool, x_pos: int, y_pos: int) -> None:
        '''Paste card image to page

        Args:
            image (PILImageType): Card image
            page (PILImageType): Page image
            has_bleed (bool): True is card has bleed in its image
            x_pos (int): top-right x pixel position to which to paste card image on page
            y_pos (int): top-right y pixel position to which to paste card image on page
        '''
        if image is None:
            return

        image = self.adjust_image(image, has_bleed)

        #Place card image onto page
        page.paste(image, (x_pos, y_pos))

        self.is_empty = False
        if self.keep_bleed:
            self.add_crop_marks(page, x_pos, y_pos)


    def update_position_on_page(self) -> tuple[int, int, int]:
        '''Calculate in which row and column next image should placed'''
        current_col = self.current_col + 1
        current_row = self.current_row

        if current_col >= self.columns:
            current_col = 0
            current_row += 1

        current_col_back = self.columns - current_col - 1

        return current_col, current_row, current_col_back


    def add_image_to_page(self, card: DoubleSidedCard) -> None:
        '''Paste a card image onto the page at the correct size.

        Args:
            card (DoubleSidedCard): Object containing data for card front and back side
        '''
        if self.page is None:
            self.page = Image.new(
                mode='RGB',
                size=(self.args.page_width, self.args.page_height),
                color=(255,255,255)
            )
        if self.has_back and self.back is None:
            self.back = Image.new(
                mode='RGB',
                size=(self.args.page_width, self.args.page_height),
                color=(255,255,255) 
            )

        #x and y are the pixel positions on the page which define where the
        #top left corner of the image will be placed.
        x, y = self.paste_position(current_col=self.current_col)
        self.paste_image(card.front.image, page=self.page, has_bleed=card.front.has_bleed, x_pos=x, y_pos=y)

        if self.back is not None and card.back is not None:
            x, y = self.paste_position(current_col=self.current_col_back)
            self.paste_image(card.back.image, page=self.back, has_bleed=card.back.has_bleed, x_pos=x, y_pos=y)

        self.current_col, self.current_row, self.current_col_back = self.update_position_on_page()

        if self.current_row >= self.rows:
            self.is_full = True




    def save_page(self, filename: Path) -> None:
        ''' Save page to disk and then clear the image data to save memory'''
        if self.page is not None:
            self.page = self.adjust_brightness(self.page)

            self.page.save(
                filename,
                subsampling=0,
                optimize=False,
                progressive=False
            )
            self.page.close()
        else:
            raise Exception("Page image is blank!")

        if self.has_back:
            if self.back is not None:
                self.back = self.adjust_brightness(self.back)

                self.back.save(
                    f"{filename.parent / filename.stem}_back{filename.suffix}",
                    subsampling=0,
                    optimize=False,
                    progressive=False
                )
                self.back.close()
            else: 
                raise Exception("Page back image is blank!")

        

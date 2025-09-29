import fpdf
import asyncio

from src.page import Page 
from src.card import DoubleSidedCard
from src.cli_args_manager import CLIArgs
from typing import Callable

import src.params as params
import src.helpers as helpers


'''
Organises DoubleSidedCard objects from src.card_maker onto pages using Page objects. 
Asynchronously adds card images to pages and saves them using a producer-consumer pattern.

Optionally also aggregates page images into a single .pdf file if set in command-line args.
'''


async def add_card_to_page(card: DoubleSidedCard, page: Page) -> None:
    '''Adds card image to page, also add back side of card to a seperate
    page, if applicable.

    Args:
        card (DoubleSidedCard): Object containing card information
        page (Page): Object containing card images
    '''
    print(f'Adding {card}')

    if not card.front.has_image:
        raise Exception(f'Image for {card.front.name} not found')

    if card.back is not None:
        if not card.back.has_image:
            raise Exception(f'Image for {card.back.name} not found')

    await asyncio.to_thread(page.add_image_to_page, card)


def release_card_images(card: DoubleSidedCard):
    '''Close pillow images after they have been added to pages to release memory'''
    if card.front is not None and card.front.image is not None:
        card.front.image.close()
    if card.back is not None and card.back.image is not None and not card.has_generic_back:
        card.back.image.close()


async def fill_pages(cards: list[DoubleSidedCard], pages: list[Page], save_queue: asyncio.Queue) -> None:
    '''Add card images to pages and enqueues pages to be saved by background workers concurrently.'''
    current_page = 1
    for card in cards:
        for _ in range(card.copies):
            page = pages[current_page - 1]

            await add_card_to_page(card, page)

            if page.is_full:
                save_queue.put_nowait((page, str(current_page)))
                current_page += 1
                continue

        release_card_images(card)

    if current_page <= len(pages):
        save_queue.put_nowait((pages[-1], str(current_page)))


def sort_pages_numerically(page_name):
    if str(page_name.stem).endswith('_back'):
        return int(page_name.stem[:-5])
    else:
        return int(page_name.stem)

def place_backs_at_end(page_name):
    if str(page_name.stem).endswith('_back'):
        return 1000
    else:
        return int(page_name.stem)


def save_pages_as_pdf(width: int, height: int, collate: bool) -> None:
    '''
    Save pages from images found in PAGE_PATH into a single pdf named cards.pdf

    Args:
        width: width each in pdf in mm
        height: height each in pdf in mm
    '''
    pdf = fpdf.FPDF(format=(width, height))
    pages = params.PAGE_PATH.iterdir()
    if collate:
        pages = sorted(pages, key=sort_pages_numerically)
    else:
        pages = sorted(pages, key=place_backs_at_end)

    for page in pages:
        pdf.add_page()
        pdf.image(str(page), x=0, y=0, w=width, h=height)
        
    pdf.output(str(params.PAGE_PATH / 'cards.pdf'))


async def save_pages(page: Page, name: str) -> None:
    '''Asynchronously save pages with naming: (name).jpg or (name)_back.jpg'''
    await asyncio.to_thread(page.save_page, params.PAGE_PATH / f'{name}.jpg')


async def page_saver(queue: asyncio.Queue) -> None:
    '''
    Saves pages to disk. Worker consumes pages from queue
    '''
    while True:
        page, name = await queue.get()
        if page is None:
            break
        await save_pages(page, name)
        queue.task_done()


def create_workers(queue: asyncio.Queue, worker_coroutine: Callable, number_of_workers: int) -> list[asyncio.Task]:
    '''Create list of workers using worker_coroutine to consume from queue.'''
    workers = [asyncio.create_task(worker_coroutine(queue)) for _ in range(number_of_workers)]
    return workers


async def shut_down_workers(workers: list[asyncio.Task]) -> None:
    '''Stops all workers'''
    for worker in workers:
        worker.cancel()

    await asyncio.gather(*workers, return_exceptions=True)


def initialise_pages(args: CLIArgs, total_pages: int, pages_with_backs: int) -> list[Page]:
    '''Create list of blank Pages'''
    pages = [
        Page(args, has_back=(i < pages_with_backs))
        for i in range(total_pages)
    ]

    return pages


def calculate_number_of_pages(cards: list[DoubleSidedCard], args: CLIArgs) -> tuple[int, int]:
    '''
    The number of pages is nontrivial since the bleed on cards, defined at runtime, 
    may cause less cards to be able to fit on pages with backs than on pages without backs.

    Args:
        card (Card): List of card object containing card information
        args (CLIArgs): Instance of data class containing normalised command-line arguments

    Returns:
        (int): Total number of pages
        (int): Number of pages that have back sides
    '''
    cards_with_backs = sum((card.back is not None) * card.copies for card in cards)
    total_cards = sum(card.copies for card in cards)

    if args.always_bleed:
        cards_with_bleed = total_cards
    elif args.no_bleed:
        cards_with_bleed = 0
    else:
        cards_with_bleed = cards_with_backs

    cols_with_bleed = args.page_width // (args.card_width + 2 * args.card_bleed_x + args.spacing_x)
    rows_with_bleed = args.page_height // (args.card_height + 2 * args.card_bleed_y + args.spacing_y)

    cols = args.page_width // (args.card_width + args.spacing_x)
    rows = args.page_height // (args.card_height + args.spacing_y)

    page_capacity_bleed = cols_with_bleed * rows_with_bleed
    page_capacity = cols * rows

    pages_with_bleed = helpers.ceiling_divide(cards_with_bleed, page_capacity_bleed)
    pages_without_bleed = helpers.ceiling_divide(total_cards - pages_with_bleed * page_capacity_bleed, page_capacity)

    pages_with_backs = helpers.ceiling_divide(cards_with_backs, page_capacity_bleed)
    total_pages = int(pages_with_bleed + pages_without_bleed)

    return total_pages, pages_with_backs


async def create_pages(args: CLIArgs, cards: list[DoubleSidedCard]) -> None:
    '''Creates pages and asynchronously populates them with card images, then saves them as a jpg
    using a producer-consumer system. 

    Args:
        args (ArgumentParser): Object containing command-line arguments.
        cards (list of Card): list of Card objects
    '''
    # Precalculate number of pages
    total_pages, pages_with_backs = calculate_number_of_pages(cards, args)

    # Create blank pages
    pages = initialise_pages(args, total_pages, pages_with_backs)

    # Create queue and workers for saving pages
    save_queue = asyncio.Queue()
    savers = create_workers(save_queue, page_saver, params.number_of_saving_workers)

    # Populate pages with card images
    await fill_pages(cards, pages, save_queue)

    # Save pages
    await save_queue.join()

    # Kill workers
    await shut_down_workers(savers)


def page_maker(args: CLIArgs, cards: list[DoubleSidedCard]):
    '''Entry point for page_maker'''
    asyncio.run(create_pages(args, cards))
    
    # Optionally save images as .pdf
    if args.save_as_pdf:
        page_width_in_mm = int(helpers.convert_pixels_to_mm(args.card_width, args.page_width))
        page_height_in_mm = int(helpers.convert_pixels_to_mm(args.card_width, args.page_height))
        save_pages_as_pdf(width=page_width_in_mm, height=page_height_in_mm, collate=args.collate_back_pages)


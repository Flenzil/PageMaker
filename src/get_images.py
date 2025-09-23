import asyncio
import aiohttp
import aiofiles
import io
import re
import base64

from PIL import Image
from PIL.Image import Image as PILImageType
from pathlib import Path
from typing import Coroutine
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn, DownloadColumn, TaskID
from src.card import Card

import src.params as params
import src.helpers as helpers
import src.exceptions as exceptions

'''
This module provides asynchronous utilities for fetching and caching images
used to represent cards. Images are sourced from Google Drive, with automatic
handling of confirmation-token redirects and download quota limits. Images
are cached locally in `params.IMAGE_PATH`, and any cached image will be
reused to avoid redundant downloads.
'''

def open_and_load_image(path:Path) -> PILImageType:
    '''Open image and ensure that Pillow loads the image into memory'''
    image = Image.open(path)
    image.load()
    return image


async def get_image_from_disk(card: Card) -> PILImageType|None:
    '''
    Load in image from IMAGE_PATH if it exists and add it to card object.

    Args:
        card (Card): object containing card info.

    Returns:
        (PILImageType|None): Image of card or None if no image found on disk
    '''
    params.IMAGE_PATH.mkdir(exist_ok=True)
    paths = [card.image_path]

    fallback_exts = [
        '.jpg',
        '.png',
        '.jpeg',
        '.tiff',
        '.bmp',
        '.gif',
        '.webp'
    ]

    fallback_paths = [
        card.image_path.with_suffix(ext)
        for ext in fallback_exts
    ]

    paths = paths + fallback_paths

    for path in paths:
        try:
            return await asyncio.to_thread(open_and_load_image, path)

        except FileNotFoundError:
            continue

        except OSError:
            #Truncated image, redownload image
            Path.unlink(path)
            break

    return None


async def update_progess_bar(
    response: aiohttp.ClientResponse, progress: Progress, task_id: TaskID, total: int
) -> bytearray:
    '''
    Extract image from response peicewise and update progress bar.

    Args:
        response (aiohttp.ClientResponse): Image response from Google Drive
        progress (Progress): Progress bar for download
        task_id (TaskID): Aliased int, ID for this download
        total (int): Expected total size for complete image

    Returns:
        (bytearray): Image pixel data
    '''
    progress.update(task_id, total=total, visible=True)
    data = bytearray()
    async for chunk in response.content.iter_chunked(params.download_chunk_size):

        if not chunk:
            return data

        data.extend(chunk)
        progress.advance(task_id, advance=len(chunk))

    return data


def handle_confirmation_page_response(response_html: str, url: str) -> str:
    '''
    Find confirmation token within confirmation page

    Args:
        response_html (str): Text content of html response from Google Drive
        url (str): url for Google Drive image download

    Returns:
        (str): modified url, now with confirmation token 
    '''

    match = re.search(r'confirm=([0-9A-Za-z_]+)', response_html)
    if match:
        confirm_token = match.group(1)
        url = ''.join([url, f'&confirm={confirm_token}'])
        return url
    else:
        raise Exception('Unable to handle non-image response')


async def handle_quota_exceeded_response(session:aiohttp.ClientSession, card: Card, headers: dict) -> bytearray:
    '''
    Use Google Script end point to fetch image as a fall back

    Args:
        session (ClientSession): Persistent aiohttp session used to perform HTTP requests.
        card (Card): Object containing card data
        headers (dict): Browser header data for request

    Returns:
        (bytearray): Image pixel data
    '''

    print(f'Download failed for {card}. Falling back to (slower) alternative method.')

    url_base = 'https://script.google.com/macros/s/AKfycbw8laScKBfxda2Wb0g63gkYDBdy8NWNxINoC4xDOwnCQ3JMFdruam1MdmNmN4wI5k4/exec'
    url = f'{url_base}?id={card.id}'

    async with session.get(url, headers=headers) as response:
        data = await response.read()
        image_type = helpers.detect_b64_image_type(await response.read())

        if image_type != 'Unknown':
            return bytearray(base64.b64decode(data))
        else:
            raise Exception('Scripts endpoint returned non-image data')


async def handle_image_response(response: aiohttp.ClientResponse, progress: Progress, task_id: TaskID) -> bytearray|None:

    '''
    Extract image data from response.

    Args:
        response (ClientResponse): The HTTP response object from aiohttp.
        progress (Progress): Progress bar object used to display download progress
        task_id (TaskID): Aliased int, id for download

    Returns:
        (bytearray|None): Raw image data or None if the image only partially downloaded
    '''

    total = int(response.headers.get('Content-Length', 0))
    data = await update_progess_bar(response, progress, task_id, total)

    if len(data) < total:
        return None

    return data


async def handle_response(response: aiohttp.ClientResponse, progress: Progress, task_id:TaskID) -> bytearray:
    '''
    Attempts to extract image data from response. Raises various errors that are
    handled in caller to trigger workarounds for various blockers e.g confirmation
    needed page or exceeded quotas.

    Args:
        response (ClientResponse): The HTTP response object from aiohttp.
        progress (Progress): Progress bar object used to display download progress
        task_id (TaskID): Aliased int, id for download

    Returns:
        (bytearray): Raw image data
    '''
    if response.status != 200:
        raise Exception(f'HTTP error: {response.status} for {response.url}')

    response_type = response.headers.get('Content-Type', '')

    if 'image' in response_type:
        card_data = await handle_image_response(response, progress, task_id)

        if card_data is None:
            raise exceptions.NoImageDataException()
        else:
            progress.update(task_id, visible=False)
            return card_data

    elif 'text' in response_type:
        html = await response.text()

        if 'Quota exceeded' in html:
            raise exceptions.QuotaExceededException()
        else:
            raise exceptions.ConfirmationNeededException()

    else:
        raise Exception(f'Unable to parse response for {response.url}')


async def download_image(session: aiohttp.ClientSession, card: Card, progress: Progress, task_id: TaskID) -> bytearray:
    '''
    Get response from google drive to extract image, even if recieving a html page.

    Args:
        session (ClientSession): Persistent aiohttp session used to perform HTTP requests.
        card (Card): Object containing card information.
        progress (Progress): Progress bar object used to display download progress
        task_id (int|None): id for progress bar

    Returns:
        (bytearray): Image data of card
    '''

    url_base = 'https://drive.google.com/uc?export=download'
    url = f'{url_base}&id={card.id}'

    cookies = None

    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                  " AppleWebKit/537.36 (KHTML, like Gecko)"
                  " Chrome/116.0.0.0 Safari/537.36"
    }

    for attempt in range(params.MAX_DOWNLOAD_RETRIES):
        async with session.get(url, cookies=cookies, headers=headers) as response:
            try:
                if card.name == 'Assert Authority':
                    raise exceptions.QuotaExceededException()

                card_data = await handle_response(response, progress, task_id)
                return card_data

            except exceptions.QuotaExceededException:
                card_data = await handle_quota_exceeded_response(session, card, headers)
                return card_data

            except exceptions.ConfirmationNeededException:
                cookies = response.cookies
                html = await response.text()
                url = handle_confirmation_page_response(html, url)

            except exceptions.NoImageDataException:
                pass

            except asyncio.exceptions.TimeoutError:
                pass

            except OSError as e:
                if 'semaphore timeout' in str(e):
                    pass
                else:
                    raise(e)


            await asyncio.sleep(min(params.backoff_mult ** attempt, params.MAX_BACKOFF))
            continue
                    
    else:
        raise Exception(f'Unable to retrieve image for {card}')


async def save_image(image: bytearray, card: Card) -> None:
    '''Asynchronously save image to IMAGE_PATH'''
    filename = card.image_path

    async with aiofiles.open(filename, 'wb') as f:
        await f.write(image)


async def get_image_from_download_or_disk(
    session: aiohttp.ClientSession, semaphore:asyncio.Semaphore, card: Card, progress: Progress, task_id: TaskID
) -> dict[str, PILImageType]:
    '''
    Either retrieve image from disk or download image if not present

    Args:
        session (ClientSession): Persistent aiohttp session used to perform HTTP requests.
        semaphore (asyncio.Semaphore): Semaphore object limiting concurrency
        card (Card): Object containing card information.
        progress (Progress): Progress bar object used to display download progress
        task_id (int|None): id for progress bar
        
    '''
    await semaphore.acquire()

    try:
        card_image = await get_image_from_disk(card)

        if card_image is None:
            card_data = await download_image(session, card, progress, task_id)

            if card_data is not None:
                await save_image(card_data, card)
                card_image = Image.open(io.BytesIO(card_data))
                card_image.load()
            else:
                card_image = Image.open(params.IMAGE_PATH.parent / "download_failed.jpg")
                card_image.load()

        return {card.id : card_image}
    finally:
        semaphore.release()


def create_task(
    session: aiohttp.ClientSession, semaphore: asyncio.Semaphore, card: Card, progress: Progress, task_id: TaskID
) -> list[Coroutine]:
    return [get_image_from_download_or_disk(session, semaphore, card, progress, task_id)]


async def find_images(cards: list[Card]) -> list[dict[str, PILImageType]]:
    '''
    Get images for each card, either by loading from IMAGE_PATH if it exists 
    and then asynchronously downloading and saving the image otherwise. 
    Set up a progress bar to display the downloads.

    Args:
        cards (list of Card): list of objects containing card information.

    Returns:
        (list[dict]): List of card ids mapped to their corresponding images
    '''

    progress_args = [
        SpinnerColumn(),
        TextColumn('[bold blue]{task.fields[name]}'),
        BarColumn(),
        DownloadColumn(),
        TimeRemainingColumn()
    ]

    semaphore = asyncio.Semaphore(params.max_simultaneous_downloads)

    async with aiohttp.ClientSession() as session:
        with Progress(*progress_args, transient=True) as progress:
            tasks = []
            for card in cards:
                task_id = progress.add_task(card.name, name=card.name, visible=False)
                tasks += create_task(session, semaphore, card, progress, task_id)

            return await asyncio.gather(*tasks)


def get_card_images(cards: list[Card]) -> dict[str, PILImageType]:
    '''
    Entry point for script

    Args:
        cards (list[Card]): list of objects containing card data

    Returns:
        (dict[str, PILImageType]): Mapping of card ID to card image

    '''
    card_images = asyncio.run(find_images(cards))
    card_images_flattened = {name: img for d in card_images for name, img in d.items()}

    return card_images_flattened

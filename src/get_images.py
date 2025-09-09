import asyncio
import aiohttp
import aiofiles
import io
import PIL
import re

from PIL import Image
from PIL.Image import Image as PILImageType
from pathlib import Path
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn, DownloadColumn, TaskID
from src.card import Card

import src.params as params

'''
This script handles downloading, verifying and assigning images to
card objects. Images are fetched from Google Drive, with support for 
confirmation-token redirects and are saved locally. Images already in
IMAGE_PATH are used whenever possible.
'''

def get_image_from_disk(card: Card, is_back: bool=False) -> PILImageType|None:
    '''
    Load in image from IMAGE_PATH if it exists and add it to card object.

    Args:
        card (Card): object containing card info.
        back (bool): True if loading backside image.

    '''
    if is_back:
        image_path = card.image_path_back
    else:
        image_path = card.image_path
    paths = [image_path]


    ppath = Path(image_path)
    fallback_paths = [
            Path(f'{ppath.parent / ppath.stem}.png'),
            Path(f'{ppath.parent / ppath.stem}.jpg'),
    ]

    for fallback_path in fallback_paths:
        if fallback_path not in paths:
            paths.append(fallback_path)

    for path in paths:
        try:
            Image.open(path).verify()
            return Image.open(path)

        except FileNotFoundError:
            continue
        except OSError:
            #Truncated image, redownload image
            Path.unlink(path)

    return None


async def save_image(image: bytearray, card: Card, is_back: bool=False):
    '''Asynchronously save image to IMAGE_PATH'''
    if is_back:
        image_path = card.image_path_back
    else:
        image_path = card.image_path

    filename = f'{Path(image_path).stem}.jpg'

    async with aiofiles.open(params.IMAGE_PATH / filename, 'wb') as f:
        await f.write(image)


async def update_progess_bar(
    response: aiohttp.ClientResponse, progress: Progress, task_id: TaskID, total: int
) -> bytearray:
    '''
    Extract image from response peicewise and update progress bar.
    '''
    progress.update(task_id, total=total, visible=True)
    CHUNK_SIZE = 1024 * 64
    data = bytearray()
    async for chunk in response.content.iter_chunked(CHUNK_SIZE):
        if not chunk:
            return data
        data.extend(chunk)
        progress.advance(task_id, advance=len(chunk))
    return data


async def limited_download(
    session: aiohttp.ClientSession,
    semaphore: asyncio.Semaphore,
    card: Card,
    progress: Progress,
    task_id: TaskID,
    is_back: bool
) -> bytearray|None:
    async with semaphore:
        return await download_image(session, card, progress, task_id, is_back)


async def get_image_from_download_or_disk(
    session: aiohttp.ClientSession, semaphore: asyncio.Semaphore, card: Card, progress: Progress, task_id: TaskID, is_back: bool=False
) -> dict[str, PILImageType]:

    '''Either retrieve image from disk or download image if not present'''

    card_image = get_image_from_disk(card, is_back=is_back)

    if card_image is None:
        card_data = await limited_download(session, semaphore, card, progress, task_id, is_back=is_back)
        if card_data is not None:
            await save_image(card_data, card, is_back=is_back)
            card_image = Image.open(io.BytesIO(card_data))
        else:
            card_image = Image.open(params.IMAGE_PATH.parent / "download_failed.jpg")

    if is_back:
        return {card.id_back : card_image}
    else:
        return {card.id : card_image}


async def handle_confirmation_page_response(response: aiohttp.ClientResponse) -> str:
    '''Find confirmation token within confirmation page'''
    html = await response.text()
    match = re.search(r'confirm=([0-9A-Za-z_]+)', str(html))
    if match:
        confirm_token = match.group(1)
        return confirm_token
    else:
        raise Exception('Unable to handle non-image response')


async def handle_quota_exceeded_response(card: Card, quota_exceeded: list[Card]) -> list[Card]:
    return quota_exceeded + [card]


async def handle_image_response(
    response: aiohttp.ClientResponse, progress: Progress, task_id: TaskID
) -> bytearray|None:

    '''
    Extract image data from response.

    Args:
        response (ClientResponse): The HTTP response object from aiohttp.
        progress (Progress): Progress bar object used to display download progress
        task_id (int): id for progress bar
    '''
    if response.status != 200:
        raise Exception(f'HTTP error: {response.status} for {response.url}')

    total = int(response.headers.get('Content-Length', 0))
    data = await update_progess_bar(response, progress, task_id, total)

    if len(data) < total:
        return None

    try:
        #return Image.open(io.BytesIO(data)).convert('RGB')
        return data
    except PIL.UnidentifiedImageError:
        raise Exception(f'{response.status}. Expected data: {total}. Actual data: {len(data)}')


async def download_image(session: aiohttp.ClientSession, card: Card, progress: Progress, task_id: TaskID, is_back: bool=False) -> bytearray|None:
    '''
    Get response from google drive to extract image, even if recieving a html page.

    Args:
        session (ClientSession): Persistent aiohttp session used to perform HTTP requests.
        card (Card): Object containing card information.
        progress (Progress): Progress bar object used to display download progress
        task_id (int): id for progress bar
        is_back (bool): True if handling backside of card

    Returns:
        (PILImageType): Image of card
    '''

    if not is_back:
        card_id = card.id
    else:
        card_id = card.id_back
    url_base = 'https://drive.google.com/uc?export=download'
    url = f'{url_base}&id={card_id}'

    MAX_BACKOFF = 30
    backoff_mult = 1.5
    cookies = None
    quota_exceeded = []

    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                  " AppleWebKit/537.36 (KHTML, like Gecko)"
                  " Chrome/116.0.0.0 Safari/537.36"
    }

    for attempt in range(params.MAX_DOWNLOAD_RETRIES):
        try:
            async with session.get(url, cookies=cookies, headers=headers) as response:
                if response.status != 200:
                    raise Exception(response)
                response_type = response.headers.get('Content-Type', '')
                if 'image' in response_type:
                    #card_image = await handle_image_response(response, progress, task_id)
                    card_data = await handle_image_response(response, progress, task_id)

                    if card_data is None:
                        await asyncio.sleep(backoff_mult ** attempt)
                        continue
                    else:
                        progress.update(task_id, visible=False)
                        return card_data
                else:
                    html = await response.text()
                    if "Quota exceeded" in html:
                        quota_exceeded = await handle_quota_exceeded_response(card, quota_exceeded)
                        progress.update(task_id, visible=False)
                        return None
                    else:
                        #Sometimes response is a html page asking for confirmation. aiohttp doesn't automatically
                        #handle redirects, so handle them here.
                        confirm_token = await handle_confirmation_page_response(response)
                        url = f'{url_base}&confirm={confirm_token}&id={card_id}'
                        cookies = response.cookies
                        await asyncio.sleep(backoff_mult ** attempt)
                        continue

        except OSError as e:
            if 'semaphore timeout' in str(e):
                await asyncio.sleep(min(backoff_mult ** attempt, MAX_BACKOFF))
                continue
            else:
                raise(e)
        except asyncio.exceptions.TimeoutError:
            await asyncio.sleep(min(backoff_mult ** attempt, MAX_BACKOFF))
            continue
    else:
        raise Exception(f'Unable to retrieve image for {card}')


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

    async with aiohttp.ClientSession() as session:
        with Progress(
            SpinnerColumn(),
            TextColumn('[bold blue]{task.fields[name]}'),
            BarColumn(),
            DownloadColumn(),
            TimeRemainingColumn(),
            transient=True,
            redirect_stdout=False,
            redirect_stderr=False
        ) as progress:
            semaphore = asyncio.Semaphore(10)
            tasks = []
            for card in cards:
                task_id = progress.add_task(card.name, name=card.name, visible=False)
                tasks.append(get_image_from_download_or_disk(session, semaphore, card, progress, task_id))

                if card.has_back:
                    if card.name_back in [t.description for t in progress.tasks]:
                        # Skip downloading the same image multiple times e.g generic card back
                        continue
                    task_id = progress.add_task(card.name_back, name=card.name_back, visible=False)
                    tasks.append(get_image_from_download_or_disk(session, semaphore, card, progress, task_id, is_back=True))

            return await asyncio.gather(*tasks)


def get_card_images(cards: list[Card]) -> dict[str, PILImageType]:
    card_images = asyncio.run(find_images(cards))
    card_images_flattened = {name: img for d in card_images for name, img in d.items()}
    return card_images_flattened

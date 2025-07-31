import asyncio
import aiohttp
import io
import PIL
import re
from PIL import Image
from pathlib import Path
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn, DownloadColumn

import params as p

ROOT = Path(__file__).resolve().parent.parent
IMAGE_PATH = Path(ROOT / "data/images")
PAGE_PATH = Path(ROOT / "pages")
XML_PATH = Path(ROOT / "data/xml")

"""
This script handles downloading, verifying and assigning images to
card objects. Images are fetched from Google Drive, with support for 
confirmation-token redirects and are saved locally. Images already in
IMAGE_PATH are used whenever possible.
"""

def get_image_from_disk(card, back=False):
    """
    Load in image from IMAGE_PATH if it exists and add it to card object.

    Args:
        card (Card): object containing card info.
        back (bool): True if loading backside image.

    """
    if not back:
        image_path = card.image_path
    else:
        image_path = card.image_path_back
    paths = [image_path]


    ppath = Path(image_path)
    fallback_path = Path(f"{ppath.parent / ppath.stem}.png")

    if fallback_path not in paths:
        paths.append(fallback_path)

    for path in paths:
        try:
            Image.open(path).verify()
            if not back:
                card.image = Image.open(path).convert('RGB')
            else:
                card.image_back = Image.open(path).convert('RGB')

        except FileNotFoundError:
            continue
        except OSError:
            #Truncated image, redownload image
            Path.unlink(path)


async def save_image(image, filename):
    """Asynchronously save image to IMAGE_PATH"""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, image.save, IMAGE_PATH / filename)

async def handle_image_response(response, card, progress, task_id, back=False):
    """
    Save image from response peicewise and update progress bar.

    Args:
        response (ClientResponse): The HTTP response object from aiohttp.
        card (Card): object containing card info
        progress (Progress): Progress bar object used to display download progress
        task_id (int): id for progress bar
        back (bool): True if handling backside of card
    """
    if response.status != 200:
        raise Exception(f"HTTP error: {response.status} for {response.url}")

    if not back:
        image_path = card.image_path
    else:
        image_path = card.image_path_back

    total = int(response.headers.get("Content-Length", 0))
    progress.update(task_id, total=total, visible=True)

    data = bytearray()
    async for chunk in response.content.iter_chunked(chunk_size := 1024):
        if not chunk:
            break
        data.extend(chunk)
        progress.advance(task_id, advance=len(chunk))

    if len(data) < total:
        return "retry"

    try:
        image = Image.open(io.BytesIO(data)).convert('RGB')
    except PIL.UnidentifiedImageError:
        raise Exception(f"{response.status}. Expected data: {total}. Actual data: {len(data)}")

    filename = f"{Path(image_path).stem}.png"
    await save_image(image, filename)

    if not back:
        card.image = image
    else:
        card.image_back = image

    progress.update(task_id, visible=False)
    return 


async def download_image(session, card, progress, task_id, back=False):
    """
    Get response from google drive to extract image, even if recieving a html page.

    Args:
        session (ClientSession): Persistent aiohttp session used to perform HTTP requests.
        card (Card): Object containing card information.
        progress (Progress): Progress bar object used to display download progress
        task_id (int): id for progress bar
        back (bool): True if handling backside of card
    """
    if not back:
        card_id = card.id
    else:
        card_id = card.id_back
    url_base = "https://drive.google.com/uc?export=download"

    url = f"{url_base}&id={card_id}"
    await asyncio.sleep(1)
    for attempt in range(p.MAX_DOWNLOAD_RETRIES):
        async with session.get(url) as initial_response:
            response_type = initial_response.headers.get("Content-Type", "")
            if "image" in response_type:
                result = await handle_image_response(initial_response, card, progress, task_id, back=back)
                if result == "retry":
                    await asyncio.sleep(1)
                    continue
                else:
                    return result
            else:
                html = await initial_response.text()

            #Sometimes response is a html page asking for confirmation. aiohttp doesn't automatically
            #handle redirects, so handle them here.
            confirm_token = None
            match = re.search(r"confirm=([0-9A-Za-z_]+)", html)
            if match:
                confirm_token = match.group(1)

            if confirm_token:
                confirm_url = f"{url_base}&confirm={confirm_token}&id={card_id}"
                cookies = initial_response.cookies
                async with session.get(confirm_url, cookies=cookies) as response:
                    result = await handle_image_response(response, card, progress, task_id, back=back)
                    if result == "retry":
                        await asyncio.sleep(1)
                        continue
                    else:
                        return result
            else:
                result = await handle_image_response(initial_response, card, progress, task_id, back=back)
                if result == "retry":
                    await asyncio.sleep(1)
                    continue
                else:
                    return result
    else:
        raise Exception(f"Unable to retireve image for {card}")


async def find_images(cards):
    """
    Get images for each card, either by loading from IMAGE_PATH if it exists 
    and then asynchronously downloading and saving the image otherwise. 
    Set up a progress bar to display the downloads.

    Args:
        cards (list of Card): list of objects containing card information.
    """

    for card in cards:
        get_image_from_disk(card)
        if card.has_back:
            get_image_from_disk(card, back=True)

    async with aiohttp.ClientSession() as session:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.fields[name]}"),
            BarColumn(),
            DownloadColumn(),
            TimeRemainingColumn(),
            transient=True,
            redirect_stdout=False,
            redirect_stderr=False
        ) as progress:
            tasks = []
            for card in cards:
                if (card.has_back and card.image and card.image_back) or (not card.has_back and card.image):
                        continue

                if card.image is None:
                    task_id = progress.add_task(card.name, name=card.name, visible=False)
                    tasks.append(download_image(session, card, progress, task_id))

                if card.has_back:
                    if card.image_back is None:
                        task_id = progress.add_task(card.name_back, name=card.name_back, visible=False)
                        tasks.append(download_image(session, card, progress, task_id, back=True))

            await asyncio.gather(*tasks)

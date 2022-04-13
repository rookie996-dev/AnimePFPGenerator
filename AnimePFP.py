import aiohttp
import secrets
import asyncio
import pyppeteer

from os import PathLike
from bs4 import BeautifulSoup
from typing import Union, Optional

__all__ = ('AsyncGetAnimePictures', 'GetAnimePictures')
__version__ = '1.0.0'

BACKSLASH = '\\'

async def AsyncGetAnimePictures(directory: Optional[Union[str, PathLike[str]]] = None, format: Optional[Union[str, bytes]] = None, stop: Optional[int] = None, *, headless: Optional[bool] = None, delay: Optional[int] = None, session: Optional[aiohttp.ClientSession] = None, semaphore: Optional[asyncio.Semaphore] = None):
    format = format or 'png'
    if isinstance(format, bytes):
        format = format.decode()
    if format.startswith('.'):
        format = format[1:]
    
    stop = stop or 10
    browser = await pyppeteer.launch(headless=headless if headless is not None else True)
    page = await browser.newPage()
    await page.goto('https://avatars.alphacoders.com/by_category/3')
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36 WAIT_UNTIL=load')

    for _ in range(stop):
        await page.evaluate(
            '''
            async () => {
                let query = await document.querySelectorAll(
                    'img'
                );
                await query[query.length - 1].scrollIntoView();
                await query[query.length - 5].scrollIntoView();
                return query.length;
            }
            '''
        )
        await page.waitFor(delay or 500)

    soup = BeautifulSoup(await page.content(), 'html.parser')
    images = [image.get('src') for image in soup.findAll('img')]

    async with semaphore or asyncio.Semaphore(20 * 10000000000):
        async with session or aiohttp.ClientSession() as request:
            for image in images:
                response = await request.get(image, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'})
                with open(f'{directory + BACKSLASH if directory else ""}{secrets.token_hex(12)}.{format}', 'wb') as file:
                    file.write(await response.read())
                file.close()

    return await request.close()

def GetAnimePictures(loop: Optional[asyncio.AbstractEventLoop] = None, directory: Optional[Union[str, PathLike[str]]] = None, format: Optional[Union[str, bytes]] = None, stop: Optional[int] = None, *, headless: Optional[bool] = None, delay: Optional[int] = None, session: Optional[aiohttp.ClientSession] = None, semaphore: Optional[asyncio.Semaphore] = None):
    loop = loop or asyncio.new_event_loop()
    return loop.run_until_complete(AsyncGetAnimePictures(directory, format, stop, headless=headless, delay=delay, session=session, semaphore=semaphore))

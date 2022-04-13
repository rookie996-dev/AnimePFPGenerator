from __future__ import annotations

import aiohttp
import secrets
import asyncio
import pyppeteer

from os import PathLike
from os.path import join
from bs4 import BeautifulSoup

__all__ = ('AsyncGetAnimePictures', 'GetAnimePictures')
__version__ = '1.0.2a'

async def AsyncGetAnimePictures(
    directory: str | PathLike[str] | None = '', 
	stop: int | None = 10, 
	*, 
	headless: bool | None = True, 
	delay: int | None = 500, 
):    
    browser = await pyppeteer.launch(headless=headless)
    page = await browser.newPage()
    await page.goto('https://avatars.alphacoders.com/by_category/3')
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36 WAIT_UNTIL=load')

    async def evaluate():
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
        await page.waitFor(delay)
        
    map(lambda _: (await evaluate() for _ in '_').__anext__(), range(stop))

    soup = BeautifulSoup(await page.content(), 'html.parser')
    images = [image.get('src') for image in soup.findAll('img')]

    async with asyncio.Semaphore(200000000):
        async with aiohttp.ClientSession() as request:
            for image in images:
                filename = secrets.token_hex(12)
                response = await request.get(image, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'})
                with open(join(directory, '{}.png'.format(filename)), 'wb') as file:
                    file.write(await response.read())
                file.close()

    return await request.close()

def GetAnimePictures(
    directory: str | PathLike[str] | None = '', 
	stop: int | None = 10, 
	*, 
	headless: bool | None = True, 
	delay: int | None = 500,
):    
    loop = asyncio.new_event_loop()
    return loop.run_until_complete(AsyncGetAnimePictures(directory, stop, headless=headless, delay=delay))

from __future__ import annotations

import os
import aiohttp
import asyncio
import pyppeteer

from tqdm import tqdm
from bs4 import BeautifulSoup

from typing import TypeVar, Generator, AsyncGenerator

_None = TypeVar('_None', type(None), type(None))
_Generator = TypeVar('_Generator', Generator, AsyncGenerator)

class AnimePicture:
    def __init__(self, data):
        self.content = data

    def save(self, directory: str = '', filename: str | None = None) -> _None:
        filename = filename or os.urandom(10).hex()
        with open(os.path.join(directory, '{}.jpg'.format(filename)), 'wb') as file:
            file.write(self.content)

        return file.close()
        
__all__ = ('AsyncGetAnimePictures', 'GetAnimePictures')
__version__ = '1.0.4'

async def AsyncGetAnimePictures(
	stop:     int   = 10, 
	*,  
	delay:    int   = 500, 
    headless: bool  = True,
) -> _Generator:    
    browser = await pyppeteer.launch(headless=headless)
    page = await browser.newPage()
    await page.goto('https://avatars.alphacoders.com/by_category/3')
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36 WAIT_UNTIL=load')

    async def scroll_down():
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
        
    for _ in tqdm(range(stop)):
        await scroll_down()

    soup = BeautifulSoup(await page.content(), 'html.parser')
    images = [image.get('src') for image in soup.findAll('img')]

    async with asyncio.Semaphore(200000000):
        async with aiohttp.ClientSession() as request:
            for image in images:
                response = await request.get(image, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'})
                yield AnimePicture(await response.read())

def GetAnimePictures(
	stop:     int   = 10, 
	*,  
	delay:    int   = 500, 
    headless: bool  = True,
) -> _Generator: 
    loop = asyncio.new_event_loop()

    async def patch():
        return [item async for item in AsyncGetAnimePictures(stop, delay=delay, headless=headless)]
    
    yield from loop.run_until_complete(patch())
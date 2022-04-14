import re
from setuptools import setup

with open('AnimePFP.py', 'r', encoding='utf-8') as file:
    code = file.read()

file.close()

version_code = re.search(r'__version__ = .*', code).group()
exec(version_code, globals(), locals())

setup(
    name='AnimePFP',
    version=__version__, # type: ignore
    description='Anime profile picture downloader using https://avatars.alphacoders.com/by_category/3',
    author='LUA9',
    maintainer='LUA9',
    url='https://github.com/LUA9/AnimePFPGenerator',
    packages=['AnimePFP'],
    requires=['aiohttp', 'pyppeteer', 'bs4', 'tqdm'],
    include_package_data=True,
)

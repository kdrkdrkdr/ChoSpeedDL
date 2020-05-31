#-*- coding:utf-8 -*-

from requests import Session, adapters
from bs4 import BeautifulSoup
from re import sub

import asyncio
import aiohttp
import aiofiles

from shutil import rmtree
from os import mkdir
from img2pdf import convert as pdfConvert

from urllib.parse import urlparse
from colorama import init, Fore
from time import time, sleep

from base64 import b64decode
from random import choice


init(autoreset=True)

loop = asyncio.get_event_loop()

sem = asyncio.Semaphore(100)




def GetSession(referer):
    sess = Session()
    sess.headers = {
        'User-Agent': 'Mozilla 5.0',
        'referer': referer,
    }

    return sess



def MakeDirectory(DirPath):
    try:
        mkdir(DirPath)
    except FileExistsError:
        rmtree(DirPath, ignore_errors=True)
        mkdir(DirPath)
    finally:
        return True



async def GetSoup(url, referer):
    sess = GetSession(referer)
    req = await loop.run_in_executor(None, sess.get, url)
    html = req.text
    soup = await loop.run_in_executor(None, BeautifulSoup, html, 'html.parser')
    return soup




async def FileDownload(filename, fileurl):
    while True:
        try:
            async with sem:
                async with aiohttp.ClientSession(headers={'User-Agent':'Mozilla 5.0'}) as sess:
                    async with sess.get(fileurl) as resp:
                        async with aiofiles.open(filename, mode='wb') as f:
                            await f.write(await resp.read())
            break

        except:
            print("다운로드 에러!")




def GetFileName(filename):
    toReplace = {
        '\\':'', '/':'', ':':'-', '\"':'',
        '?':'', '<':'[', '>':']', '|':'-', '*':''
    }

    for key, value in toReplace.items():
        filename = str(filename).replace(key, value)

    return filename



def MakePDF(ImageList, Filename):
    try:
        with open(Filename, 'wb') as pdf:
            pdf.write(pdfConvert(ImageList))
    except:
        StatePrint('error', 'pdf 제작에 오류가 발생했습니다.')

    finally:
        return
        




def StatePrint(state, string):
    if state == 'info':
        print(Fore.YELLOW + f'[Info] {string}')

    elif state == 'error':
        print(Fore.RED + f'[Error] {string}')

    elif state == 'complete':
        print(Fore.GREEN + f'[Complete] {string}')

    elif state == 'download':
        print(Fore.CYAN + f'[Download] {string} 다운로드 중...')

    elif state == 'time':
        print(Fore.WHITE + f'[Time] 다운로드 시간(초): {int(string)}')

    elif state == 'dir':
        print(Fore.YELLOW + f'[File] 폴더 위치: \"{string}\"')

    else:
        print("?")

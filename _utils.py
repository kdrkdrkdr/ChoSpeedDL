#-*- coding:utf-8 -*-

from requests import Session
from bs4 import BeautifulSoup
from re import sub

import asyncio
import aiohttp
import aiofiles

from img2pdf import convert as pdfConvert
from shutil import rmtree
from os import mkdir

from urllib.parse import urlparse
from colorama import init, Fore
from time import time, sleep

init(autoreset=True)

sem = asyncio.Semaphore(5)

loop = asyncio.get_event_loop()



def GetSession(url, referer):
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
    sess = GetSession(url, referer)
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




def MakePDF(ImageList, Filename, DirLoc):
    try:
        with open(Filename, 'wb') as pdf:
            pdf.write(pdfConvert(ImageList))
    except:
        StatePrint('error', 'pdf 제작에 오류가 발생했습니다.')

    finally:
        rmtree(DirLoc, ignore_errors=True)




def GetFileName(filename):
    toReplace = {
        '\\':'', '/':'', ':':'-', '\"':'',
        '?':'', '<':'[', '>':']', '|':'-', '*':''
    }

    for key, value in toReplace.items():
        filename = str(filename).replace(key, value)

    return filename




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

    elif state == 'file':
        print(Fore.YELLOW + f'[File] 파일 이름: \"{string}\"')

    else:
        print("?")

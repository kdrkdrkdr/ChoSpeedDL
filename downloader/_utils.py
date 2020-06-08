#-*- coding:utf-8 -*-

from requests import Session, adapters
from bs4 import BeautifulSoup
from re import sub

import asyncio
import aiohttp
import aiofiles

from shutil import rmtree
from os import mkdir, system
from img2pdf import convert as pdfConvert

from urllib.parse import urlparse
from colorama import init, Fore
from time import time, sleep

from base64 import b64decode
from random import choice
import codecs

from json import loads
from click import clear as ClearWindow
from threading import Thread

from pySmartDL import SmartDL
from os.path import isfile, isdir


download_folder = '다운로드_폴더'


init(autoreset=True)


sem = asyncio.Semaphore(250)

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
        pass

    finally:
        return True



async def GetSoup(url, referer, loop):
    sess = GetSession(referer)
    req = await loop.run_in_executor(None, sess.get, url)
    html = req.text
    soup = await loop.run_in_executor(None, BeautifulSoup, html, 'html.parser')
    return soup




def BigFileDownload(filename, dirLoc, fileurl, referer=None):
    ariaLocation = '.\\util\\aria2c.exe '
    
    ariaCmd = ariaLocation + ' '.join(
        [
            f'--out={filename}',
            f'--dir={dirLoc}',
            '--file-allocation=none',
            '--check-certificate=false',
            '--max-connection-per-server=16',
            '--split=64',
            '--min-split-size=1M',
            '--user-agent="Mozilla 5.0"',
            # f'--referer={referer}'
            fileurl
        ]
    )
    
    system('start /b ' + ariaCmd)



async def FileDownload(filename, fileurl, referer=None):
    if referer == None:
        referer = fileurl
        
    while True:
        try:
            async with sem:
                async with aiohttp.ClientSession(headers={'User-Agent':'Mozilla 5.0', 'Referer':referer}) as sess:
                    async with sess.get(fileurl) as resp:
                        async with aiofiles.open(filename, 'wb') as f:
                            await f.write(await resp.read())
            break

        except:
            continue



def GetFileName(filename):
    toReplace = {
        '\\':'', '/':'', ':':'-', '\"':'', '-':'_',
        '?':'', '<':'[', '>':']', '|':'-', '*':'',
        '\n':'', '\t':'', '        ':'', ' ':'_'
    }

    for key, value in toReplace.items():
        filename = str(filename).replace(key, value)

    return filename



async def MakePDF(ImageList, Filename):
    try:
        async with aiofiles.open(Filename, 'wb') as pdf:
            await pdf.write(pdfConvert(ImageList))
    except:
        StatePrint('error', f'pdf 제작에 오류가 발생했습니다. => {Filename}')

    finally:
        return
        
        

def WriteTextFile(filename, content):
    f = codecs.open(filename, 'w', encoding='utf-8')
    f.write(content)
    f.close()




def StatePrint(state, string):
    if state == 'info':
        print(Fore.YELLOW + f'[Info] {string}')

    elif state == 'error':
        print(Fore.RED + f'\n[Error] {string}')

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

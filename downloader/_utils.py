#-*- coding:utf-8 -*-

from requests import Session, adapters
from bs4 import BeautifulSoup
from re import sub

import asyncio
import aiohttp
import aiofiles

from shutil import rmtree
from os import mkdir, system, remove
from PIL import Image

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
from PyPDF2 import PdfFileMerger


download_folder = '다운로드_폴더'


init(autoreset=True)


sem = asyncio.Semaphore(50)

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




def BigFileDownload(filename, fileurl, referer=None):
    while True:
        try:
            obj = SmartDL(fileurl, dest=filename, progress_bar=True, request_args={'headers':{'user-agent':'Mozilla/5.0', 'referer':referer}}, threads=100)
            obj.start()
            break
        except:
            StatePrint('error', "다운로드중에 에러가 발생했습니다.")



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



async def TempPDF(make_count, temp_pdfs, Filename, idx):
    image1 = Image.open(make_count[idx][0])
    image1.convert('RGB')

    images = []
    for j in make_count[idx][1:]:
        a = Image.open(j)
        a.convert("RGB")
        images.append(a)

    image1.save(temp_pdfs[idx], save_all=True, append_images=images)


async def MakePDF(ImageList, Filename):

    ilen = len(ImageList)

    seper = 15

    tpdf_count = ilen // seper + 1

    make_count = [ImageList[i*seper: (i+1)*seper] for i in range(tpdf_count)]
    temp_pdfs = [Filename.replace('.pdf', f'_{i}.pdf') for i in range(tpdf_count)]

    tasks = [asyncio.ensure_future(TempPDF(make_count, temp_pdfs, Filename, i)) for i in range(tpdf_count)]
    await asyncio.gather(*tasks)
    
    merger = PdfFileMerger()

    for i in temp_pdfs:
        merger.append(i)

    merger.write(Filename)
    merger.close()
    
    for r in temp_pdfs: remove(f'./{r}')

        

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

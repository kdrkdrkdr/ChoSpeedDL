
from downloader._utils import ( urlparse, StatePrint, mkdir, download_folder, ClearWindow, sleep, asyncio )
from downloader import *
from downloader import _utils

from os.path import isdir, isfile
from os import system

import ctypes
import sys
from threading import Thread


def run_executor(import_file, content_url):
    import_file.run(content_url)



def check_requirements_file():
    if isdir(f'./{download_folder}/'):
        pass

    else:
        mkdir(f'./{download_folder}/')




def goodbye_dpi():
    system('.\\util\\goodbyedpi.exe -1')
    pass



def main(content_url):
    check_requirements_file()

    base_url = urlparse(content_url).netloc

    if 'e-hentai.org' in base_url: run_executor(dl_ehentai, content_url)
    elif 'comic.naver.com' in base_url: run_executor(dl_naverwt, content_url)
    elif 'tkor' in base_url: run_executor(dl_toonkor, content_url)
    elif 'ncode.syosetu.com' in base_url: run_executor(dl_syosetu, content_url)
    elif 'hiyobi' in base_url: run_executor(dl_hiyobi, content_url)
    elif 'marumaru' in base_url: run_executor(dl_marumaru, content_url)
    elif 'pixiv.net' in base_url: run_executor(dl_pixiv, content_url)
    elif 'yaani24' in base_url: run_executor(dl_yaani24, content_url)
    elif 'ani24' in base_url: run_executor(dl_ani24, content_url)

    else: StatePrint('error', '지원되지 않는 사이트 입니다.')



if __name__ == "__main__":
    
    if ctypes.windll.shell32.IsUserAnAdmin():
        thr = Thread(target=goodbye_dpi)
        thr.start()
        
        sleep(1)
        ClearWindow()

        while True:
            content_url = str(input('\n>> ')).replace(' ', '')
            mainThr = Thread(target=main, args=(content_url,))
            mainThr.start()
        

        system('taskkill /f /im goodbyedpi.exe')
        thr.join()


    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
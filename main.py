
from downloader._utils import ( loop, urlparse, StatePrint, mkdir, download_folder, ClearWindow, sleep )
from downloader import *

from os.path import isdir
from os import system

import ctypes
import sys
from threading import Thread


def run_executor(import_file, content_url):
    loop.run_until_complete(import_file.main(content_url))




def check_download_folder():
    if isdir(f'./{download_folder}/'):
        return

    else:
        mkdir(f'./{download_folder}/')



def goodbye_dpi():
    system('.\\goodbyedpi\\goodbyedpi.exe -1')



def main():
    while True:
        try:
            check_download_folder()

            content_url = str(input('\n>> ')).replace(' ', '')
            base_url = urlparse(content_url).netloc
            

            if 'e-hentai.org' in base_url: run_executor(dl_ehentai, content_url)
            elif 'comic.naver.com' in base_url: run_executor(dl_naverwt, content_url)
            elif 'tkor' in base_url: run_executor(dl_toonkor, content_url)
            elif 'ncode.syosetu.com' in base_url: run_executor(dl_syosetu, content_url)
            elif 'hiyobi' in base_url: run_executor(dl_hiyobi, content_url)
            elif 'marumaru' in base_url: run_executor(dl_marumaru, content_url)

            else: StatePrint('error', '지원되지 않는 사이트 입니다.')



        except ( KeyboardInterrupt, EOFError ):
            break

    loop.close()




if __name__ == "__main__":
    
    if ctypes.windll.shell32.IsUserAnAdmin():
        thr = Thread(target=goodbye_dpi)
        thr.start()
        
        sleep(1)
        ClearWindow()
        main()

        system('taskkill /f /im goodbyedpi.exe')
        thr.join()

    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
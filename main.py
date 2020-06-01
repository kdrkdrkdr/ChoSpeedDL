
from downloader._utils import loop, urlparse, StatePrint, mkdir

from downloader import *

from os.path import isdir


def run_executor(import_file, content_url):
    loop.run_until_complete(import_file.main(content_url))


def check_download_folder():
    if isdir('./다운로드_폴더/'):
        return

    else:
        mkdir('./다운로드_폴더/')



def main():
    while True:
        try:
            check_download_folder()

            content_url = str(input('\n: ')).replace(' ', '')
            base_url = urlparse(content_url).netloc
            

            if 'e-hentai.org' in base_url: run_executor(dl_ehentai, content_url)
            elif 'comic.naver.com' in base_url: run_executor(dl_naverwt, content_url)
            elif 'tkor' in base_url: run_executor(dl_toonkor, content_url)
            elif 'ncode.syosetu.com' in base_url: run_executor(dl_syosetu, content_url)


            else: StatePrint('error', '지원되지 않는 사이트 입니다.')



        except ( KeyboardInterrupt, EOFError ):
            break

    loop.close()



if __name__ == "__main__":
    main()
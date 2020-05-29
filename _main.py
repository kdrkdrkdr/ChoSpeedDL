
from _utils import loop, urlparse, StatePrint

from _downloader import *


def run_executor(import_file, content_url):
    loop.run_until_complete(import_file.main(content_url))
    loop.close()


def main():
    while True:
        try:
            content_url = str(input('\n: ')).replace(' ', '')
            base_url = urlparse(content_url).netloc
            

            try:
                if 'e-hentai' in base_url: run_executor(dl_ehentai, content_url)
                elif 'comic.naver.com' in base_url: run_executor(dl_naverwt, content_url)
                elif 'tkor' in base_url: run_executor(dl_toonkor, content_url)

                else: StatePrint('error', '지원되지 않는 사이트 입니다.')

            except:
                pass



        except ( KeyboardInterrupt, EOFError ):
            break



if __name__ == "__main__":
    main()
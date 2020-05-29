from _utils import *

async def GetImagesURL(epi_url):
    soup = await GetSoup(epi_url, referer=epi_url)
    
    h2 = soup.find_all('h2')[1]
    for s in h2.select('span'):
        s.extract()

    bigTitle = h2.text

    wtitle = soup.h3.text
    ListOfIMGsURL = [i['src'] for i in soup.find('div', {'class':'wt_viewer'}).find_all('img')]
    return [bigTitle, wtitle, ListOfIMGsURL]



async def main(wtLink):
    start_time = time()

    StatePrint('info', '다운로드 중...')

    wt = await GetImagesURL(wtLink)

    wtTitle = wt[1]
    imgsURL = wt[2]
    
    dirLoc = GetFileName(f'{wtTitle}')
    MakeDirectory(dirLoc)

    imgLoc = [f'./{dirLoc}/naver_wt_temp_{i}.jpg' for i in range(len(imgsURL))]


    tasks = [asyncio.ensure_future(FileDownload(filename=f'./{dirLoc}/naver_wt_temp_{idx}.jpg', fileurl=imgUrl)) for idx, imgUrl in enumerate(imgsURL)]
    await asyncio.gather(*tasks)

    fname = dirLoc + '.pdf'

    MakePDF(
        ImageList=imgLoc,
        Filename=fname,
        DirLoc=dirLoc
    )

    StatePrint('time', f'{int(time()-start_time)}')
    StatePrint('file', f'{fname}')
    StatePrint('complete', '다운로드 완료!')
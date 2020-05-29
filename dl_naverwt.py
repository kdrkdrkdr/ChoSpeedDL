from _utils import *

async def GetImagesURL(epi_url):
    StatePrint("info", "정보를 불러오는 중..")

    ListOfIMGsURL = []

    soup = await GetSoup(epi_url, referer=epi_url)

    h2 = soup.find_all('h2')[1]
    for t in h2.select('span'):
        t.extract()

    title = sub('[\n\t]', '', h2.text)
    
    epiCount = int(str(soup.find('td', {'class':'title'}).a['onclick']).split("\'")[-2])
    pages = (epiCount // 10) + 1

    pageUrls = [f'{epi_url}&page={i}' for i in range(1, pages+1, 1)]
    pSoup = [asyncio.ensure_future(GetSoup(u, referer=u)) for u in pageUrls]
    p = await asyncio.gather(*pSoup)

    episode_linkList = []
    for q in p[::-1]:
        episode_linkList.extend(q.find_all('td', {'class':'title'})[::-1])

    episode_links = ['https://comic.naver.com' + e.a['href'] for e in episode_linkList]

    rSoup = [asyncio.ensure_future(GetSoup(r, referer=r)) for r in episode_links]
    r = await asyncio.gather(*rSoup)

    for s in r:
        ListOfIMGsURL.extend(i['src'] for i in s.find('div', {'class':'wt_viewer'}).find_all('img'))

    return [title, ListOfIMGsURL]




async def main(wtLink):
    start_time = time()

    StatePrint('info', '다운로드 중...')

    wt = await GetImagesURL(wtLink)

    wtTitle = wt[0]
    imgsURL = wt[1]
    
    dirLoc = GetFileName(f'{wtTitle}')
    MakeDirectory(dirLoc)

    imgLoc = [f'./{dirLoc}/naver_wt_temp_{i}.jpg' for i in range(len(imgsURL))]


    tasks = [asyncio.ensure_future(FileDownload(filename=f'./{dirLoc}/naver_wt_temp_{idx}.jpg', fileurl=imgUrl)) for idx, imgUrl in enumerate(imgsURL)]
    await asyncio.gather(*tasks)

    fname = '[naver-wt]' + dirLoc + '.pdf'

    MakePDF(
        ImageList=imgLoc,
        Filename=fname,
        DirLoc=dirLoc
    )

    StatePrint('time', f'{int(time()-start_time)}')
    StatePrint('file', f'{fname}')
    StatePrint('complete', '다운로드 완료!')
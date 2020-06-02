from ._utils import *


baseURL = 'https://comic.naver.com'


async def GetImagesURL(epi_url, loop):

    ListOfIMGsURL = {}

    soup = await GetSoup(epi_url, referer=epi_url, loop=loop)

    h2 = soup.find_all('h2')[1]
    for t in h2.select('span'):
        t.extract()

    title = sub('[\n\t]', '', h2.text)
    
    epiCount = int(str(soup.find('td', {'class':'title'}).a['onclick']).split("\'")[-2])
    pages = (epiCount // 10) + 1

    pageUrls = [f'{epi_url}&page={i}' for i in range(1, pages+1, 1)]
    pSoup = [asyncio.ensure_future(GetSoup(u, referer=u, loop=loop)) for u in pageUrls]
    p = await asyncio.gather(*pSoup)

    episode_linkList = []
    for q in p[::-1]:
        episode_linkList.extend(q.find_all('td', {'class':'title'})[::-1])

    episode_links = ['https://comic.naver.com' + e.a['href'] for e in episode_linkList]

    rSoup = [asyncio.ensure_future(GetSoup(r, referer=r, loop=loop)) for r in episode_links]
    r = await asyncio.gather(*rSoup)

    for s in r:
        ListOfIMGsURL[s.h3.text] = [i['src'] for i in s.find('div', {'class':'wt_viewer'}).find_all('img')]


    return [title, ListOfIMGsURL]




async def main(wtLink, loop):
    start_time = time()

    wt = await GetImagesURL(wtLink, loop)

    wtTitle = wt[0]
    imgsURL = wt[1]
    
    dirLoc = '[naver-wt] ' + GetFileName(f'{wtTitle}')
    MakeDirectory(f'./{download_folder}/{dirLoc}/')

    dirList = []
    imageLoc = []
    tasks = []
    for k, v in imgsURL.items():
        MakeDirectory(f'./{download_folder}/{dirLoc}/{k}/')
        dirList.append(f'./{download_folder}/{dirLoc}/{k}')

        tempDir = []
        for idx, imgUrl in enumerate(v):
            imgFileName = f'./{download_folder}/{dirLoc}/{k}/{idx}.jpg'
            tasks.append(asyncio.ensure_future(FileDownload(filename=imgFileName, fileurl=imgUrl)))
            tempDir.append(imgFileName)

        imageLoc.append(tempDir)


    await asyncio.gather(*tasks)


    pdf_tasks = [asyncio.ensure_future(MakePDF(ImageList=imageLoc[idx], Filename=dirList[idx]+'.pdf')) for idx in range(len(dirList))]
    
    await asyncio.gather(*pdf_tasks)
    
    for d in dirList: rmtree(d, ignore_errors=True)


def run(gLink):
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main(gLink, loop))
    loop.close()


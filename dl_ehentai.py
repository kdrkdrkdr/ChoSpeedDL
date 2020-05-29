from _utils import (
    asyncio,
    GetSoup,
    sub,
    time,
    MakeDirectory,
    MakePDF,
    FileDownload,
    GetFileName,
    StatePrint
)


async def GetDirectImagesURL(temp_image_urls:list):
    aSoup = [asyncio.ensure_future(GetSoup(t, referer=t)) for t in temp_image_urls]
    a = await asyncio.gather(*aSoup)
    realImg = [i.find('img', {'id':'img'})['src'] for i in a]
    return realImg



async def GetImagesURL(gallery_url):
    tempImageList = []

    pSoup = await GetSoup(gallery_url, referer=gallery_url)
    pages = (int(sub('[\D]', '', pSoup('td', {'class':'gdt2'})[5].text)) // 40) + 1

    gTitle = pSoup.find('h1', {'id':'gn'}).text

    urls = [f'{gallery_url}/?p={p}' for p in range(pages)]
    rSoup = [asyncio.ensure_future(GetSoup(u, referer=u)) for u in urls]
    r = await asyncio.gather(*rSoup)

    for i in r:
        aTag = i.find('div', {'id':'gdt'}).find_all('a')
        tempImageList.extend([a['href'] for a in aTag])

    realImageList = await GetDirectImagesURL(tempImageList)

    return [gTitle, realImageList]



async def main(gallery_link):
    
    start_time = time()

    StatePrint('info', f'download {gallery_link}')
    StatePrint('info', '다운로드 중..')

    g = await GetImagesURL(gallery_link)
    gTitle = g[0]
    imgsURL = g[1]

    dirLoc = GetFileName(f'{gTitle}')

    MakeDirectory(f'./{dirLoc}/')

    imgLoc = [f'./{dirLoc}/e_hentai_temp_{i}.jpg' for i in range(len(imgsURL))]


    tasks = [asyncio.ensure_future(FileDownload(filename=f'./{dirLoc}/e_hentai_temp_{idx}.jpg', fileurl=imgurl)) for idx, imgurl in enumerate(imgsURL)]
    await asyncio.gather(*tasks)

    fname = dirLoc + '.pdf'
    
    MakePDF(
        ImageList=imgLoc,
        Filename=fname,
        DirLoc = f'./{dirLoc}/'
    )
    
    StatePrint('time', f'{int(time()-start_time)}')
    StatePrint('file', f'{fname}')
    StatePrint('complete', '다운로드 완료!')

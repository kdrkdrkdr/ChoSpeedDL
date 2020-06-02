from ._utils import *


baseURL = 'https://e-hentai.org'


async def GetDirectImagesURL(temp_image_urls, loop):
    aSoup = [asyncio.ensure_future(GetSoup(t, referer=t, loop=loop)) for t in temp_image_urls]
    a = await asyncio.gather(*aSoup)
    realImg = [i.find('img', {'id':'img'})['src'] for i in a]
    return realImg




async def GetImagesURL(gallery_url, loop):
    
    tempImageList = []

    pSoup = await GetSoup(gallery_url, referer=gallery_url, loop=loop)
    pages = (int(sub('[\D]', '', pSoup('td', {'class':'gdt2'})[5].text)) // 40) + 1

    gTitle = pSoup.find('h1', {'id':'gn'}).text

    urls = [f'{gallery_url}/?p={p}' for p in range(pages)]
    rSoup = [asyncio.ensure_future(GetSoup(u, referer=u, loop=loop)) for u in urls]
    r = await asyncio.gather(*rSoup)

    for i in r:
        aTag = i.find('div', {'id':'gdt'}).find_all('a')
        tempImageList.extend([a['href'] for a in aTag])

    realImageList = await GetDirectImagesURL(tempImageList, loop)

    return [gTitle, realImageList]



async def main(gallery_link, loop):
    
    start_time = time()

    g = await GetImagesURL(gallery_link, loop)


    gTitle = g[0]
    imgsURL = g[1]

    dirLoc = '[e-hentai] ' + GetFileName(f'{gTitle}')

    MakeDirectory(f'./{download_folder}/{dirLoc}/')

    imageLoc = []
    tasks = []
    for idx, imgurl in enumerate(imgsURL):
        imgName = f'./{download_folder}/{dirLoc}/{idx}.jpg'
        tasks.append(asyncio.ensure_future(FileDownload(filename=imgName, fileurl=imgurl)))
        imageLoc.append(imgName)
        
    
    await asyncio.gather(*tasks)

    await asyncio.gather(asyncio.ensure_future(MakePDF(ImageList=imageLoc, Filename=f'./{download_folder}/{dirLoc}.pdf')))

    rmtree(f'./{download_folder}/{dirLoc}/', ignore_errors=True)



def run(gLink):
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main(gLink, loop))
    loop.close()

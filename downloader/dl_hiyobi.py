from ._utils import *

baseURL = 'https://cdn.hiyobi.me'


async def GetImagesURL(gLink, loop):

    g_num = sub('[\D]', '', gLink)

    soup = await GetSoup(f'https://cdn.hiyobi.me/data/json/{g_num}_list.json', referer=baseURL, loop=loop)
    json = loads(soup.text)

    data_url = 'https://cdn.hiyobi.me/data/' + g_num + '/'
    imgList = [data_url+i['name'] for i in json]

    tSoup = await GetSoup(f'https://api.hiyobi.me/gallery/{g_num}', referer='https://api.hiyobi.me', loop=loop)
    title = loads(tSoup.text)['title']

    return [title, imgList]




async def main(gLink, loop):
    g = await GetImagesURL(gLink, loop)

    title = g[0]
    imgsURL = g[1]

    dirLoc = '[hiyobi] ' + GetFileName(f'{title}')
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
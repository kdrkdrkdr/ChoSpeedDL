from ._utils import *

baseURL = 'https://pixiv.net'

async def GetImageURL(artLink):

    art_id = sub('[\D]', '', artLink)

    soup = await GetSoup(f'https://www.pixiv.net/ajax/illust/{art_id}', referer=baseURL)

    illustJsonContent = loads(soup.text)

    illust_url = illustJsonContent['body']['urls']['original']
    illust_title = illustJsonContent['body']['title']

    return [illust_title, illust_url]


async def main(artLink):
    g = await GetImageURL(artLink)

    fname = '[pixiv] ' + GetFileName(g[0]) + '.jpg'
    imgurl = g[1]

    task = asyncio.ensure_future(FileDownload(filename=f'{download_folder}/{fname}', fileurl=imgurl))
    await asyncio.gather(task)
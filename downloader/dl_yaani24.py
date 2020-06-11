from ._utils import *


baseURL = 'https://yaani24.net'


async def GetOneVideoURL(aniLink, loop):
    soup = await GetSoup(aniLink, referer=baseURL, loop=loop)
    
    epiTitle = soup.find('div', {'class':'view_info_box'}).find_all('div')[0].text
    bigTitle = ' '.join(epiTitle.split(' ')[0:-1])

    link = soup.find('video', {'id':'video'})['src']

    return [bigTitle, {epiTitle:link}]



async def GetVideosURL(aniLink, loop):
    ListOfVideosURL = {}

    soup = await GetSoup(aniLink, referer=baseURL, loop=loop)
    info = soup.find('div', {'class':'ani_video_list'}).find_all('a')

    bigTitle = soup.h1.text

    epiUrls = [baseURL + i['href'] for i in info]
    epiTitles = [i.img['alt'] for i in info]

    tasks = [asyncio.ensure_future(GetSoup(u, referer=baseURL, loop=loop)) for u in epiUrls]
    
    ySoup = await asyncio.gather(*tasks)

    links = [y.find('video', {'id':'video'})['src'] for y in ySoup]
    
    for idx in range(len(links)):
        ListOfVideosURL[epiTitles[idx]] = links[idx]


    return [bigTitle, ListOfVideosURL]





async def main(aniLink, loop):
    if 'ani_view' in aniLink:
        g = await GetOneVideoURL(aniLink, loop)
    else:
        g = await GetVideosURL(aniLink, loop)


    aniTitle = g[0]
    aniVideoList = g[1]


    dirLoc = '[yaani24]' + GetFileName(aniTitle)
    MakeDirectory(f'./{download_folder}/{dirLoc}')

    thrList = []
    for k, v in aniVideoList.items():
        fname = f'./{download_folder}/{dirLoc}/{GetFileName(k)}.mp4'
        if isfile(fname) != True:
            thrList.append(
                Thread(target=BigFileDownload, args=(f'./{download_folder}/{dirLoc}/{GetFileName(k)}.mp4', v, baseURL))
            )

    for thr in thrList:
        thr.start()
        thr.join()



def run(aniLink):
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main(aniLink, loop))
    loop.close()
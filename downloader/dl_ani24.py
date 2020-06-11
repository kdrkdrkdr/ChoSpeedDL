from ._utils import *


baseURL = 'https://ani24do.com'



async def GetOneVideoURL(aniLink, loop):
    soup = await GetSoup(aniLink, referer=aniLink, loop=loop)

    epiTitle = soup.find('div', {'class':'view_info_box'}).find_all('div')[0].text
    bigTitle = ' '.join(epiTitle.split(' ')[0:-1])

    epiIDs = aniLink.split('/ani_view/')[1].replace('.html', '')

    task = []
    eSoup = task.append(asyncio.ensure_future(
        GetSoup(
            f'https://fileiframe.com/ani_video4/{epiIDs}.html?player=',
            referer=f'https://ani24do.com/ani_view/{epiIDs}.html',
            loop=loop
        )
    ))
    e = await asyncio.gather(*task)
    
    link = e[0].find('div', {'class':'player_button'}).find('button', {'class':'link_button link_video'})['data-link']

    return [bigTitle, {epiTitle:link}]



async def GetVideoURL(aniLink, loop):
    ListOfVideosURL = {}

    soup = await GetSoup(aniLink, referer=aniLink, loop=loop)

    bigTitle = soup.find('h1', {'class':'ani_info_title_font_box'}).text

    epiUrls = [baseURL + l['href'] for l in soup.find('div', {'class':'ani_video_list'}).find_all('a')]
    epiIDs = [i.split('/ani_view/')[1].replace('.html', '') for i in epiUrls]

    titleList = [t.text for t in soup.find_all('div', {'class':'subject'})]

    tasks_aniURL = []
    for i in epiIDs:
        tasks_aniURL.append(
            asyncio.ensure_future(
                GetSoup(
                    f'https://fileiframe.com/ani_video4/{i}.html?player=',
                    referer=f'https://ani24do.com/ani_view/{i}.html',
                    loop=loop
                )
            )
        )
    lSoup = await asyncio.gather(*tasks_aniURL)
    
    links = [u.find('div', {'class':'player_button'}).find('button', {'class':'link_button link_video'})['data-link'] for u in lSoup]
        
        
    for idx in range(len(links)):
        ListOfVideosURL[titleList[idx]] = links[idx]

    return [bigTitle, ListOfVideosURL]





async def main(aniLink, loop):
    
    if 'ani_view' in aniLink:
        g = await GetOneVideoURL(aniLink, loop)
    else:
        g = await GetVideoURL(aniLink, loop)

    aniTitle = g[0]
    aniVideoList = g[1]

    dirLoc = '[ani24]' + GetFileName(aniTitle)
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
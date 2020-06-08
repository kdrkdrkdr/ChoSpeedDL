from ._utils import *

baseURL = 'https://marumaru.earth'



async def GetOneEpisode(epi_url, loop):
    soup = await GetSoup(epi_url, referer=epi_url, loop=loop)

    epiTitle = soup.find('meta', {'name':'title'})['content']
    bigTitle = ' '.join(epiTitle.split(' ')[0:-1])

    print(epiTitle)

    imgs = [i['src'] if 'marumaru' in i['src'] else baseURL+i['src'] for i in soup.find('div', {'class':'view-img'}).find_all('img')]

    return [bigTitle, {epiTitle:imgs}]




async def GetImagesURL(epi_url, loop):
    
    ListOfIMGsURL = {}

    soup = await GetSoup(epi_url, referer=epi_url, loop=loop)

    title = soup.h1.text

    episode_linkList = [baseURL + i.a['href'] for i in soup.find_all('td', {'class':'list-subject'})]

    elSoup = [asyncio.ensure_future(GetSoup(el, referer=el, loop=loop)) for el in episode_linkList]
    e = await asyncio.gather(*elSoup)

    for j in e:
        ListOfIMGsURL[j.find('meta', {'name':'title'})['content']] = [i['src'] if 'marumaru' in i['src'] else baseURL+i['src'] for i in j.find('div', {'class':'view-img'}).find_all('img')]

    return [title, ListOfIMGsURL]



async def main(epi_url, loop):
    
    g = await GetOneEpisode(epi_url, loop)

    title = g[0]
    imgsURL = g[1]

    dirLoc = '[marumaru] ' + GetFileName(f'{title}')
    MakeDirectory(f'./{download_folder}/{dirLoc}/')
    
    dirList = []
    imageLoc = []
    tasks = []
    for k, v in imgsURL.items():
        if isfile(f'./{download_folder}/{dirLoc}/{k}.pdf') != True:
            MakeDirectory(f'./{download_folder}/{dirLoc}/{k}/')
            dirList.append(f'./{download_folder}/{dirLoc}/{k}')

            tempDir = []
            for idx, imgUrl in enumerate(v):
                imgFileName = f'./{download_folder}/{dirLoc}/{k}/{idx}.jpg'
                tasks.append(asyncio.ensure_future(FileDownload(filename=imgFileName, fileurl=imgUrl, referer=baseURL)))
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

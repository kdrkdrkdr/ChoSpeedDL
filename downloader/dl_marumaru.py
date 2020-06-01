from ._utils import *

baseURL = 'https://marumaru.guide'

async def GetImagesURL(epi_url):
    
    ListOfIMGsURL = {}

    soup = await GetSoup(epi_url, referer=epi_url)

    title = soup.h1.text

    episode_linkList = [baseURL + i.a['href'] for i in soup.find_all('td', {'class':'list-subject'})]

    elSoup = [asyncio.ensure_future(GetSoup(el, referer=el)) for el in episode_linkList]
    e = await asyncio.gather(*elSoup)

    for j in e:
        ListOfIMGsURL[j.find('meta', {'name':'title'})['content']] = [i['src'] if 'marumaru' in i['src'] else baseURL+i['src'] for i in j.find('div', {'class':'view-img'}).find_all('img')]

    return [title, ListOfIMGsURL]



async def main(epi_url):

    g = await GetImagesURL(epi_url)

    title = g[0]
    imgsURL = g[1]

    dirLoc = '[marumaru] ' + GetFileName(f'{title}')
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
    

    for idx in range(len(dirList)):
        MakePDF(
            ImageList=imageLoc[idx],
            Filename=dirList[idx] + '.pdf',
        )
    
    for d in dirList: rmtree(d, ignore_errors=True)
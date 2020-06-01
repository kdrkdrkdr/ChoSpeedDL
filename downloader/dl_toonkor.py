from ._utils import *


baseURL = 'https://tkor.pro'

async def GetImagesURL(wtLink):

    ListOfIMGsURL = {}

    soup = await GetSoup(wtLink, referer=wtLink)

    wtTitle = soup.find('td', {'class':'bt_title'}).text

    try:
        table = list(soup.find('table', {'class':'web_list'}).find_all('tr', {'class':'tborder'}))
        table.reverse()
    except (AttributeError, TypeError):
        pass


    epiUrls = [baseURL + t.find('td', {'class':'episode__index'})['data-role'] for t in table]

    eSoup = [asyncio.ensure_future(GetSoup(e, referer=baseURL)) for e in epiUrls]

    t = await asyncio.gather(*eSoup)

    for f in t:
        tempDir = []

        b64Code = f.text.split("var toon_img = ")[1].split(";")[0]
        html = b64decode(b64Code.encode("UTF-8")).decode("UTF-8")
        IMGsCode = BeautifulSoup(html, 'html.parser').find_all("img")

        for imgURL in IMGsCode:
            imgSrc  = imgURL['src']

            if len(imgSrc.split('/data/')[0].replace(' ', '')) != 0:
                tempDir.append(imgSrc)
            else:
                tempDir.append(baseURL + imgSrc)

        ListOfIMGsURL[f.h1.text] = tempDir

    return [wtTitle, ListOfIMGsURL]



async def main(wtLink):
    start_time = time()
    wt = await GetImagesURL(wtLink)

    wtTitle = wt[0]
    imgsURL = wt[1]

    dirLoc = '[toonkor] ' + GetFileName(f'{wtTitle}')
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
            Filename=dirList[idx] + '.pdf'
        )
    
    for d in dirList: rmtree(d, ignore_errors=True)
    
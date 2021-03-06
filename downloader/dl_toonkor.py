from ._utils import *


baseURL = 'https://tkor.pro'

async def GetOneEpisode(wtLink, loop):
    
    soup = await GetSoup(wtLink, referer=wtLink, loop=loop)

    epiTitle = soup.h1.text

    bigTitle = ' '.join(epiTitle.split(' ')[0:-1])
    imgsURL = []

    b64Code = soup.text.split("var toon_img = ")[1].split(";")[0]
    html = b64decode(b64Code.encode("UTF-8")).decode("UTF-8")
    IMGsCode = BeautifulSoup(html, 'html.parser').find_all("img")

    for imgURL in IMGsCode:
        imgSrc  = imgURL['src']

        if len(imgSrc.split('/data/')[0].replace(' ', '')) != 0:
            imgsURL.append(imgSrc)
        else:
            imgsURL.append(baseURL + imgSrc)

    return [bigTitle, {epiTitle:imgsURL}]


async def GetImagesURL(wtLink, loop):

    ListOfIMGsURL = {}

    soup = await GetSoup(wtLink, referer=wtLink, loop=loop)

    wtTitle = soup.find('td', {'class':'bt_title'}).text

    try:
        table = list(soup.find('table', {'class':'web_list'}).find_all('tr', {'class':'tborder'}))
        table.reverse()
    except (AttributeError, TypeError):
        pass


    epiUrls = [baseURL + t.find('td', {'class':'episode__index'})['data-role'] for t in table]

    eSoup = [asyncio.ensure_future(GetSoup(e, referer=baseURL, loop=loop)) for e in epiUrls]

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



async def main(wtLink, loop):
    start_time = time()

    if '.html' in wtLink:
        wt = await GetOneEpisode(wtLink, loop)
    
    else:
        wt = await GetImagesURL(wtLink, loop)

    wtTitle = wt[0]
    imgsURL = wt[1]

    dirLoc = '[toonkor] ' + GetFileName(f'{wtTitle}')
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
    
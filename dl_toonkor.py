from _utils import *


baseURL = 'https://tkor.pro'

async def GetImagesURL(wtLink):
    StatePrint("info", "정보를 불러오는 중..")

    ListOfIMGsURL = []

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
        b64Code = f.text.split("var toon_img = ")[1].split(";")[0]
        html = b64decode(b64Code.encode("UTF-8")).decode("UTF-8")
        IMGsCode = BeautifulSoup(html, 'html.parser').find_all("img")

        for imgURL in IMGsCode:
            imgSrc  = imgURL['src']

            if len(imgSrc.split('/data/')[0].replace(' ', '')) != 0:
                ListOfIMGsURL.append(imgSrc)
            else:
                ListOfIMGsURL.append(baseURL + imgSrc)

    return [wtTitle, ListOfIMGsURL]



async def main(wtLink):
    start_time = time()

    StatePrint('info', '다운로드 중...')

    wt = await GetImagesURL(wtLink)

    wtTitle = wt[0]
    imgsURL = wt[1]

    dirLoc = GetFileName(f'{wtTitle}')
    MakeDirectory(dirLoc)

    imgLoc = [f'./{dirLoc}/tkor_temp_{i}.jpg' for i in range(len(imgsURL))]

    tasks = [asyncio.ensure_future(FileDownload(filename=f'./{dirLoc}/tkor_temp_{idx}.jpg', fileurl=imgUrl)) for idx, imgUrl in enumerate(imgsURL)]
    await asyncio.gather(*tasks)


    fname = '[toonkor]' + dirLoc + '.pdf'

    MakePDF(
        ImageList=imgLoc,
        Filename=fname,
        DirLoc=dirLoc
    )

    StatePrint('time', f'{int(time()-start_time)}')
    StatePrint('file', f'{fname}')
    StatePrint('complete', '다운로드 완료!')

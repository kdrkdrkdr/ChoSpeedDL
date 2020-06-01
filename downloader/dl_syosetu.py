from ._utils import *

baseURL = 'https://ncode.syosetu.com'

async def GetEpisURL(syosetuLink):
    StatePrint('info', '정보를 불러오는 중..')

    ListOfEpisURL = {}

    soup = await GetSoup(syosetuLink, referer=baseURL)

    bigTitle = soup.find('p', {'class':'novel_title'}).text
    index = soup.find('div', {'class':'index_box'}).find_all('dl')

    for i in index:
        nUrl = baseURL + i.find('a')['href']
        nTitle = i.find('a').text    

        ListOfEpisURL[nTitle] = nUrl

    return [bigTitle, ListOfEpisURL]



async def main(syosetuLink):
    start_time = time()

    epi_list = await GetEpisURL(syosetuLink)

    syosetuTitle = epi_list[0]
    epi_urls = epi_list[1]

    dirLoc = '[syosetu] ' + GetFileName(syosetuTitle)
    MakeDirectory(f'./다운로드_폴더/{dirLoc}/')
    
    tasks = [asyncio.ensure_future(GetSoup(v, referer=baseURL)) for k, v in epi_urls.items()]
    ncode = await asyncio.gather(*tasks)

    for idx, n in enumerate(ncode):
        novelContent = ""

        nContent = n.find('div', {'id':'novel_honbun'}).find_all('p')
        for nC in nContent:
            novelContent += str(nC.text) + "\n"
        
        WriteTextFile(filename=f'./다운로드_폴더/{dirLoc}/{list(epi_urls.keys())[idx]}.txt', content=novelContent)

    StatePrint('time', f'{int(time()-start_time)}')
    StatePrint('dir', f'./다운로드_폴더/{dirLoc}/')
    StatePrint('complete', '다운로드 완료!')
from ._utils import *

baseURL = 'https://ncode.syosetu.com'

async def GetEpisURL(syosetuLink, loop):
    ListOfEpisURL = {}

    soup = await GetSoup(syosetuLink, referer=baseURL, loop=loop)

    bigTitle = soup.find('p', {'class':'novel_title'}).text
    index = soup.find('div', {'class':'index_box'}).find_all('dl')

    for i in index:
        nUrl = baseURL + i.find('a')['href']
        nTitle = i.find('a').text    

        ListOfEpisURL[nTitle] = nUrl

    return [bigTitle, ListOfEpisURL]



async def main(syosetuLink, loop):

    start_time = time()

    epi_list = await GetEpisURL(syosetuLink, loop)

    syosetuTitle = epi_list[0]
    epi_urls = epi_list[1]

    dirLoc = '[syosetu] ' + GetFileName(syosetuTitle)
    MakeDirectory(f'./{download_folder}/{dirLoc}/')
    
    tasks = [asyncio.ensure_future(GetSoup(v, referer=baseURL, loop=loop)) for k, v in epi_urls.items()]
    ncode = await asyncio.gather(*tasks)

    for idx, n in enumerate(ncode):
        novelContent = ""

        nContent = n.find('div', {'id':'novel_honbun'}).find_all('p')
        for nC in nContent:
            novelContent += str(nC.text) + "\n"
        
        WriteTextFile(filename=f'./{download_folder}/{dirLoc}/{list(epi_urls.keys())[idx]}.txt', content=novelContent)


def run(gLink):
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main(gLink, loop))
    loop.close()
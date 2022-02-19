from bs4 import BeautifulSoup
import asyncio
import aiohttp
from fake_useragent import UserAgent
import lxml
from random import choice
proxy_list = open("http_proxies.txt").readlines()
class Parser:
    def __init__(self):
        self.basic_url = "https://storgom.ua"
        self.main_catalog_links = []
        self.sub_catalog_links = []
        self.ua = UserAgent()
        self.headers = {
            "accept": "*/*",
            "user-agent": self.ua.random
        }
    async def get_main_catalog_links(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(url = self.basic_url, headers = self.headers) as response:
                html = await response.text()
                soup = BeautifulSoup(html, "lxml")
                catalog_links = soup.find('div', id = 'catalog-menu').find_all('li', class_ = 'd-flex')
                for linksa in catalog_links:
                    a = linksa.find("a")
                    href = a['href']
                    url = f'{self.basic_url}{href}'
                    self.main_catalog_links.append(url)
        print(self.main_catalog_links)

    async def get_all_catalog_links(self, session, link, num):
                async with session.get(url = link, headers=self.headers) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, "lxml")
                    sub_catalog_links = soup.find_all('a', class_ = 'd-flex')
                    for sublink in sub_catalog_links:
                        href = sublink['href']
                        url = f'{self.basic_url}{href}'
                        self.sub_catalog_links.append(url)

    async def gather_all_catalog_tasks(self):
        async with aiohttp.ClientSession() as session:
            all_catalog_tasks = []
            for num, link in enumerate(self.main_catalog_links):
                task = asyncio.create_task(self.get_all_catalog_links(session, link, num))
                all_catalog_tasks.append(task)
            await asyncio.gather(*all_catalog_tasks)


    def main(self):
        asyncio.get_event_loop().run_until_complete(self.get_main_catalog_links())
        asyncio.get_event_loop().run_until_complete(self.gather_all_catalog_tasks())
        print(self.sub_catalog_links)

if __name__ == "__main__":
    parser = Parser()
    parser.main()
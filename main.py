from bs4 import BeautifulSoup
import asyncio
import aiohttp
from fake_useragent import UserAgent
import lxml

class Parser:
    def __init__(self):
        self.basic_url = "https://storgom.ua"
        self.main_catalog_links = []
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
                for link in catalog_links:
                    a = link.find("a")
                    href = a['href']
                    url = f'{self.basic_url}{href}'
                    self.main_catalog_links.append(url)
        print(self.main_catalog_links)
    def main(self):
        asyncio.get_event_loop().run_until_complete(self.get_main_catalog_links())


if __name__ == "__main__":
    parser = Parser()
    parser.main()
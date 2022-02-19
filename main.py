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
        self.all_links_category = []
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

    async def get_pagination(self):
        async with aiohttp.ClientSession() as session:
            for link in self.sub_catalog_links[0:15]:
                async with session.get(url=link, headers=self.headers) as response:
                    try:
                        html = await response.text()
                        soup = BeautifulSoup(html, "lxml")
                        pagination = soup.find("div", class_ = "pagination").find_all("li")
                        if pagination==None:
                            print(f'link IF{link}')
                        else:
                            # print(f'PAGINATION ELSE{pagination}')
                            # print(f'LAST:{pagination[-2]}')
                            page_first = pagination[-2].find('a')
                            # print(f'PAGE_FIRST{page_first}')
                            last_page = page_first.text
                            # print(last_page)
                            page_first_href = page_first['href']
                            link_page_first = page_first_href.split('/')[1]
                            page_first_url = f'{self.basic_url}/{link_page_first}.html'
                            self.all_links_category.append(page_first_url)
                            for i in range(2, int(last_page)+1):
                                url_with_pagination =f'{self.basic_url}/{link_page_first}/page-{i}.html'
                                print(url_with_pagination)
                                self.all_links_category.append(url_with_pagination)


                    except:
                        # print(f'EXEPT LINK{link}')
                        self.all_links_category.append(link)




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
        asyncio.get_event_loop().run_until_complete(self.get_pagination())
        print(self.all_links_category)

if __name__ == "__main__":
    parser = Parser()
    parser.main()
from bs4 import BeautifulSoup
import asyncio
import aiohttp
from fake_useragent import UserAgent
import lxml
import
class Parser:
    def __init__(self):
        self.basic_url = "https://storgom.ua"
        self.main_catalog_links = []
        self.sub_catalog_links = []
        self.all_links_category = []
        self.all_products_links = []
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
    async def get_pagination(self, session, link, num):
            async with session.get(url=link, headers=self.headers) as response:
                try:
                    html = await response.text()
                    soup = BeautifulSoup(html, "lxml")
                    pagination = soup.find("div", class_ = "pagination").find_all("li")
                    page_first = pagination[-2].find('a')
                    print(f'PAGE_FIRST{page_first}')
                    last_page = page_first.text
                    print(last_page)
                    page_first_href = page_first['href']
                    link_page_first = page_first_href.split('/')[1]
                    page_first_url = f'{self.basic_url}/{link_page_first}.html'
                    self.all_links_category.append(page_first_url)
                    for i in range(2, int(last_page)+1):
                        url_with_pagination = f'{self.basic_url}/{link_page_first}/page-{i}.html'
                        print(url_with_pagination)
                        self.all_links_category.append(url_with_pagination)
                except:
                    print(f'EXEPT LINK{link}')
                    self.all_links_category.append(link)
    async def gather_all_catalog_tasks(self):
        async with aiohttp.ClientSession() as session:
            all_catalog_tasks = []
            for num, link in enumerate(self.main_catalog_links):
                task = asyncio.create_task(self.get_all_catalog_links(session, link, num))
                all_catalog_tasks.append(task)
            await asyncio.gather(*all_catalog_tasks)
    async def gather_pagination_tasks(self):
        async with aiohttp.ClientSession() as session:
            pagination_task = []
            for num, link in enumerate(self.sub_catalog_links[0:15]):
                task = asyncio.create_task(self.get_pagination(session, link, num))
                pagination_task.append(task)
            await asyncio.gather(*pagination_task)
    async def get_pages_products(self, session, link, num):
                async with session.get(url = link, headers = self.headers) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'lxml')
                    products_link = soup.find_all('div', class_ = 'products-list_item-wrap')
                    for i in products_link:
                        link = i.find('a')
                        href = link['href']
                        url = f'{self.basic_url}{href}'
                        print(url)
                        self.all_products_links.append(url)
    async def gather_pages_tasks(self):
        async with aiohttp.ClientSession() as session:
            pages_tasks = []
            for num, link in enumerate(self.all_links_category[0:15]):
                task = asyncio.create_task(self.get_pages_products(session, link, num))
                pages_tasks.append(task)
            await asyncio.gather(*pages_tasks)
    async def load_products(self, session, link, num):
                async with session.get(url = link, headers = self.headers) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'lxml')
                    try:
                        h1 = soup.h1.string.strip()
                        print(h1)
                    except:
                        pass
                    try:
                        sku_div = soup.find('div', class_ = 'sku')
                        sku = sku_div.find('span').text.strip()
                        sku_stru = f'{sku}STRU'
                        print(sku_stru)
                    except:
                        print('net artikula')
                    try:
                        old_price_raw = soup.find('div', 'old-price').text.strip()
                        old_price = old_price_raw.replace(' ', '')
                        print(old_price)
                    except:
                        print('net old price')
                    try:
                        new_price_raw = soup.find('div', 'new-price').text.strip()
                        new_price_without_cur = new_price_raw.replace('₴', '')
                        new_price = new_price_without_cur.replace(' ', '')
                        print(new_price)
                    except:
                        print('net new price')
                    try:
                        regular_price_raw = soup.find('div', 'price').text.strip()
                        regular_price_without_cur = regular_price_raw.replace('₴', '')
                        regular_price = new_price_without_cur.replace(' ', '')
                        print(regular_price)
                    except:
                        print('net obucnoj cenu')
                    try:
                        available = soup.find('div', class_ = 'status').text.strip()
                        print(available)
                    except:
                        print('net nalichia')

    async def gather_load_products_tasks(self):
        async with aiohttp.ClientSession() as session:
            load_pages_tasks = []
            for num, link in enumerate(self.all_products_links[0:10]):
                task = asyncio.create_task(self.load_products(session, link, num))
                load_pages_tasks.append(task)
            await asyncio.gather(*load_pages_tasks)

    def write_to_csv(self):
        print("Writing csv")

        with open("test.csv", "w", encoding="utf-8") as file:
            headers = ["title", "price", "discount",
                       "num_scores", "rating", "link"]
            w = csv.DictWriter(file, headers)
            w.writeheader()
            for row in self.csv_rows:
                w.writerow(row)
    def main(self):
        asyncio.get_event_loop().run_until_complete(self.get_main_catalog_links())
        asyncio.get_event_loop().run_until_complete(self.gather_all_catalog_tasks())
        asyncio.get_event_loop().run_until_complete(self.gather_pagination_tasks())
        asyncio.get_event_loop().run_until_complete(self.gather_pages_tasks())
        asyncio.get_event_loop().run_until_complete(self.gather_load_products_tasks())
        print(self.all_products_links)
if __name__ == "__main__":
    parser = Parser()
    parser.main()
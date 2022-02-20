from bs4 import BeautifulSoup
import asyncio
import aiohttp
from fake_useragent import UserAgent
import lxml
import xlsxwriter
import time
class Parser:
    def __init__(self):
        self.basic_url = "https://storgom.ua"
        self.main_catalog_links = []
        self.sub_catalog_links = []
        self.all_links_category = []
        self.all_products_links = []
        self.name_product = []
        self.sku_product = []
        self.old_price_list = []
        self.new_price_list = []
        self.regular_price_list = []
        self.available_list = []
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
                    last_page = page_first.text
                    page_first_href = page_first['href']
                    link_page_first = page_first_href.split('/')[1]
                    page_first_url = f'{self.basic_url}/{link_page_first}.html'
                    self.all_links_category.append(page_first_url)
                    for i in range(2, int(last_page)+1):
                        url_with_pagination = f'{self.basic_url}/{link_page_first}/page-{i}.html'
                        self.all_links_category.append(url_with_pagination)
                except:
                    print(f'EXEPT LINK:{link}')
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
            for num, link in enumerate(self.sub_catalog_links):
                task = asyncio.create_task(self.get_pagination(session, link, num))
                pagination_task.append(task)
            await asyncio.gather(*pagination_task)
    async def get_pages_products(self, session, link, num):
        try:
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
        except:
            print('Сброшен запрос1')
    async def gather_pages_tasks(self):
        async with aiohttp.ClientSession() as session:
            pages_tasks = []
            for num, link in enumerate(self.all_links_category):
                task = asyncio.create_task(self.get_pages_products(session, link, num))
                pages_tasks.append(task)
            await asyncio.gather(*pages_tasks)
    async def load_products(self, session, link, num):
        try:
            async with session.get(url = link, headers = self.headers) as response:
                print(link)
                html = await response.text()
                soup = BeautifulSoup(html, 'lxml')
                try:
                    h1 = soup.h1.string.strip()
                    self.name_product.append(h1)
                except:
                    pass
                try:
                    sku_div = soup.find('div', class_ = 'sku')
                    sku = sku_div.find('span').text.strip()
                    sku_stru = f'{sku}STRU'
                    self.sku_product.append(sku_stru)
                except:
                    print('net artikula')
                try:
                    price_block = soup.find('div', 'price-wrapper')
                except:
                    print('НЕТ БЛОКА')
                try:
                    old_price_raw = price_block.find('div', 'old-price').text.strip()
                    old_price = old_price_raw.replace(' ', '')
                    self.old_price_list.append(old_price)
                except:
                    regular_price_raw = price_block.text.strip()
                    regular_price_without_cur = regular_price_raw.replace('₴', '')
                    regular_price = regular_price_without_cur.replace(' ', '')
                    regi = regular_price.split('\n')[0]
                    self.old_price_list.append(regi)

                try:
                    new_price_raw = price_block.find('div', 'new-price').text.strip()
                    new_price_without_cur = new_price_raw.replace('₴', '')
                    new_price = new_price_without_cur.replace(' ', '')
                    self.new_price_list.append(new_price)
                except:
                    regular_price_raw1 = price_block.text.strip()
                    regular_price_without_cur1 = regular_price_raw1.replace('₴', '')
                    regular_price1 = regular_price_without_cur1.replace(' ', '')
                    regi1 = regular_price1.split('\n')[0]
                    self.new_price_list.append(regi1)
                try:
                    available = soup.find('div', class_ = 'status').text.strip()
                    self.available_list.append(available)
                except:
                    print('net nalichia')
        except:
            print('СБРОШЕН ЗАПРОС')

    async def gather_load_products_tasks(self):
        async with aiohttp.ClientSession() as session:
            load_pages_tasks = []
            for num, link in enumerate(self.all_products_links):
                task = asyncio.create_task(self.load_products(session, link, num))
                print(f'load products{task}')
                load_pages_tasks.append(task)
            await asyncio.gather(*load_pages_tasks)

    def write_to_csv(self):
        print("zapis v xls")
        workbook = xlsxwriter.Workbook('demo.xlsx')
        worksheet = workbook.add_worksheet()
        row_prod = 0
        row_sku = 0
        row_old_price = 0
        row_new_price = 0
        row_available= 0
        for item in self.name_product:
            worksheet.write(row_prod, 0, item)
            row_prod += 1
        for item2 in self.sku_product:
            worksheet.write(row_sku, 1, item2)
            row_sku += 1
        for item3 in self.old_price_list:
            worksheet.write(row_old_price, 2, item3)
            row_old_price += 1
        for item4 in self.new_price_list:
            worksheet.write(row_new_price, 3, item4)
            row_new_price += 1
        for item5 in self.available_list:
            worksheet.write(row_available, 4, item5)
            row_available += 1
        workbook.close()
    def main(self):
        start_time = time.time()
        asyncio.get_event_loop().run_until_complete(self.get_main_catalog_links())
        asyncio.get_event_loop().run_until_complete(self.gather_all_catalog_tasks())
        asyncio.get_event_loop().run_until_complete(self.gather_pagination_tasks())
        asyncio.get_event_loop().run_until_complete(self.gather_pages_tasks())
        asyncio.get_event_loop().run_until_complete(self.gather_load_products_tasks())
        self.write_to_csv()
        finish_time = time.time() - start_time
        print(f"\n\nTime to finish: {finish_time}")
if __name__ == "__main__":
    parser = Parser()
    parser.main()
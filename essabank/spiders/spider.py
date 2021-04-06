import scrapy

from scrapy.loader import ItemLoader

from ..items import EssabankItem
from itemloaders.processors import TakeFirst
import requests

url = "https://www.essabank.com/services/news_service.php"

payload="page_id=499&detail=news&cats=%3A%3A237%3A%3A%2C&instance=646&cat=&limit=99999&start=0"
headers = {
  'Connection': 'keep-alive',
  'Pragma': 'no-cache',
  'Cache-Control': 'no-cache',
  'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
  'Accept': '*/*',
  'X-Requested-With': 'XMLHttpRequest',
  'sec-ch-ua-mobile': '?0',
  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
  'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'Origin': 'https://www.essabank.com',
  'Sec-Fetch-Site': 'same-origin',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Dest': 'empty',
  'Referer': 'https://www.essabank.com/about/news/press-releases/',
  'Accept-Language': 'en-US,en;q=0.9,bg;q=0.8',
  'Cookie': 'COCC_WebHosting=u0021G2FoyzVl6QBj7ZyyJVTMCrvFtENQ96IpZCQ7I3pVrJ+sgWp8EtYnpFwsnszw98saZh3qOgYyU3kd9gi//x9hyTzXmKS4K+7nUeDU3uc=; PHPSESSID=932nu1k8uv7s1pmvaghdk78e1f97nlu3khbbfs44qrrcn229hdn0; _gcl_au=1.1.1074715275.1617624307; _ga=GA1.2.1075680542.1617624307; _gid=GA1.2.1080574181.1617624307; _ce.s=v11.rlc~1617624308351; sc_last_visit=Mon%2C+05+Apr+2021+08%3A06%3A20+-0400; _gat=1; COCC_WebHosting=!8RlxhP3ZJ5nKb+myJVTMCrvFtENQ99I39tkTLP6Evsr6HGu598xgIuBP7tCAUj4hThqNsVayWDu927CPeoK2tUSO4zQPy/s6JPm+bsA='
}


class EssabankSpider(scrapy.Spider):
	name = 'essabank'
	start_urls = ['https://www.essabank.com/about/news/press-releases/']

	def parse(self, response):
		data = requests.request("POST", url, headers=headers, data=payload)
		raw_data = scrapy.Selector(text=data.text)

		post_links = raw_data.xpath('//a[@title="Read More"]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

	def parse_post(self, response):
		print(response)
		title = response.xpath('//h1[@class="page-title"]/text()').get()
		description = response.xpath('//div[@class="l-content"]//text()[normalize-space() and not(ancestor::h4)]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()
		date = response.xpath('//div[@class="l-content"]//h4/text()').get()

		item = ItemLoader(item=EssabankItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()

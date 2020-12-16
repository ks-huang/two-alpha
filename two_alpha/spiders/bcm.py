import random
import scrapy
from scrapy.loader import ItemLoader
from two_alpha.items import ReloadingItem

class BcmSpider(scrapy.Spider):
    name = 'BravoCompany'
    preproc_urls = {
        # 12.5" upper
        'https://bravocompanyusa.com/12-5-carbine-upper-group/?{}&{}' :
        ['_bc_fsnf=1', 'in_stock=1'],

        # 300 BO
        'https://bravocompanyusa.com/bcm-upper-receiver-groups-300-blackout/' : [],
    }

    def __init__(self):
        self.start_urls = []
        for url, args in self.preproc_urls.items():
            random.shuffle(args)
            self.start_urls.append(url.format(*args))

        super().__init__

    def parse(self, response):
        for item in response.xpath('//ul[has-class("productGrid")]/li'):
            if not item.xpath('.//h5[has-class("card-out-of-stock")]'):
                il = ItemLoader(item=ReloadingItem(), selector=item)
                il.add_xpath('product_name', 'normalize-space(.//h4[has-class("card-title")]/a[not(contains(@rel, "nofollow"))]/text())')
                il.add_xpath('url', './/h4[has-class("card-title")]/a[not(contains(@rel, "nofollow"))]/@href')
                yield il.load_item() if il.load_item() else None

        next_button = response.xpath('//li[has-class("pagination-item pagination-item--next")]')
        if next_button.get() is not None:
            next_page = next_button.xpath('a/@href').get()
            yield response.follow(next_page, self.parse)

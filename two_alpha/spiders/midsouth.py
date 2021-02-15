import random
import scrapy
from scrapy.loader import ItemLoader
from scrapy.http import Request
from two_alpha.items import ReloadingItem
from two_alpha.spiders.two_alpha_spider import TwoAlphaSpider

class MidsouthSpider(TwoAlphaSpider):
    name = 'MidsouthShootersSupply'
    preproc_urls = {
        # Primers
        'https://www.midsouthshooterssupply.com/dept/reloading/primers' : [],

        # 9mm bullet
        'https://www.midsouthshooterssupply.com/dept/reloading/pistol-bullets/-point-355-dia' : [],

        # .30 bullet
        'https://www.midsouthshooterssupply.com/dept/reloading/rifle-bullets/-point-308-dia?instock=true&grain={}gr,{}gr,{}gr,{}gr&brand=sierra-bullets' :
        ['125', '168' ,'180', '220'],
    }

    def __init__(self):
        self.start_urls = []
        for url, args in self.preproc_urls.items():
            random.shuffle(args)
            self.start_urls.append(url.format(*args))

        super().__init__

    def parse(self, response):
        for item in response.xpath('//div[has-class("product")]'):
            if not item.xpath('.//span[has-class("out-of-stock")]'):
                il = ItemLoader(item=ReloadingItem(), selector=item)
                il.add_xpath('product_name', 'normalize-space(.//div[has-class("product-description")]/a[not(contains(@rel, "nofollow"))]/text())')
                url = item.xpath('.//div[has-class("product-description")]/a[not(contains(@rel, "nofollow"))]/@href').get()
                il.add_value('url', response.urljoin(url))
                yield il.load_item() if il.load_item() else None

        next_button = response.xpath('//div[has-class("pagination")]//a[not(has-class("aspNetDisabled")) and text()="Next"]')
        if next_button.get() is not None:
            next_page = next_button.xpath('@href').get()
            yield response.follow(next_page, self.parse)

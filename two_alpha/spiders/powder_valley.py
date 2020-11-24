import random
import scrapy
from scrapy.loader import ItemLoader
from two_alpha.items import ReloadingItem

class PowderValleySpider(scrapy.Spider):
    name = 'PowderValley'
    args = [
        [125, 180, 220, random.randint(100,250)],
        ['cci', 'federal-reloading-supplies', 'cc' + chr(random.randint(ord('a'), ord('z')))],
        ['300-aac-blackout','308-win', '{}-win'.format(random.randint(301, 999))]
    ]

    start_urls = [
        ('https://www.powdervalleyinc.com/product-category/reloading-supplies/bullets/rifle/'
         '?query_type_grain-weight=or&filter_grain-weight={}-gr%2C{}-gr%2C{}-gr%2C{}-gr&'
         'filter_caliber-range-sort-by=307-309&query_type_caliber-range-sort-by=or&filter_brand=sierra&query_type_brand=or'),
        ('https://www.powdervalleyinc.com/product-category/reloading-supplies/primers/?query_type_product-type=or'
         '&filter_brand={}%2C{}%2C{}&query_type_brand=or&filter_product-type=small-rifle-primers'),
        ('https://www.powdervalleyinc.com/product-category/reloading-supplies'
         '/brass/rifle-brass/?filter_caliber-range-sort-by={}%2C{}%2C{}&query_type_caliber-range-sort-by=or'),
    ]

    def __init__(self):
        for ix in range(len(self.start_urls)):
            random.shuffle(self.args[ix])
            self.start_urls[ix] = self.start_urls[ix].format(*self.args[ix])

        super().__init__

    def parse(self, response):
        for item in response.xpath('//ul[has-class("products columns-3")]/li'):
            if not item.xpath('a/p[has-class("out-of-stock")]'):
                il = ItemLoader(item=ReloadingItem(), selector=item)
                il.add_xpath('product_name', 'a/h2/text()')
                il.add_xpath('url', 'a[not(contains(@rel, "nofollow"))]/@href')
                yield il.load_item() if il.load_item() else None

        next_button = response.xpath('//span[has-class("pager-text right")]')
        if next_button.get() is not None:
            next_page = next_button.xpath('../@href').get()
            yield response.follow(next_page, self.parse)

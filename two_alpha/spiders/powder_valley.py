import random
import scrapy
from scrapy.loader import ItemLoader
from two_alpha.items import ReloadingItem

class PowderValleySpider(scrapy.Spider):
    name = 'PowderValley'
    preproc_urls = {
        # bullets
        ('https://www.powdervalleyinc.com/product-category/reloading-supplies/bullets/rifle/'
         '?query_type_grain-weight=or&filter_grain-weight={}-gr%2C{}-gr%2C{}-gr%2C{}-gr%2C{}-gr&'
         'filter_caliber-range-sort-by=307-309&query_type_caliber-range-sort-by=or&filter_brand=sierra&query_type_brand=or') :
        [125, 180, 168, 220, random.randint(231,250)],

        ('https://www.powdervalleyinc.com/product-category/reloading-supplies/bullets/pistol/'
         '?query_type_grain-weight=or&filter_grain-weight={}-gr%2C{}-gr&'
         'filter_caliber-range-sort-by=355-358&query_type_caliber-range-sort-by=or&query_type_brand=or') :
         [115, random.randint(241,280)],

        # primers
        ('https://www.powdervalleyinc.com/product-category/reloading-supplies/primers/?query_type_product-type=or'
         '&filter_brand={}%2C{}%2C{}&query_type_brand=or&filter_product-type=small-rifle-primers') :
        ['cci', 'federal-reloading-supplies', 'cc' + chr(random.randint(ord('a'), ord('z')))],

        # brass
        ('https://www.powdervalleyinc.com/product-category/reloading-supplies'
         '/brass/rifle-brass/?filter_caliber-range-sort-by={}%2C{}%2C{}&query_type_caliber-range-sort-by=or') :
        ['300-aac-blackout','308-win', '{}-win'.format(random.randint(301, 999))],

        # powder
	('https://www.powdervalleyinc.com/product-category/reloading-supplies/powder/smokeless-powder/?{}&{}&{}&{}') :
	['filter_brand=hodgdon-powder', 'query_type_brand=or', 'filter_product-type=smokeless-powder', 'query_type_product-type=or'],
    }

    def __init__(self):
        self.start_urls = []
        for url, args in self.preproc_urls.items():
            random.shuffle(args)
            self.start_urls.append(url.format(*args))

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

import scrapy
from scrapy.loader import ItemLoader
from two_alpha.items import ReloadingItem

class PowderValleySpider(scrapy.Spider):
    name = 'PowderValley'
    start_urls = [
        ('https://www.powdervalleyinc.com/product-category/reloading-supplies'
         '/brass/rifle-brass/?filter_caliber-range-sort-by=300-aac-blackout'),
        ('https://www.powdervalleyinc.com/product-category/reloading-supplies'
         '/primers/?filter_product-type=large-rifle-primers%2Csmall-rifle-primers'
         '&query_type_product-type=or&query_type_brand=or&filter_brand=cci%2Cfederal-reloading-supplies'),
        ('https://www.powdervalleyinc.com/product-category/reloading-supplies/'
          'bullets/rifle/?query_type_grain-weight=or&filter_grain-weight=125-gr%2C168-gr%2C180-gr%2C220-gr'
          '&filter_caliber-range-sort-by=307-309&query_type_caliber-range-sort-by=or&filter_brand=sierra&query_type_brand=or')
    ]

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
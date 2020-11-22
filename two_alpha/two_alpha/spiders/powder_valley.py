import scrapy

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
        for item in response.css('ul.products.columns-3').xpath('li'):
            if item.css('p.stock.out-of-stock').get() is None:
                yield {
                    'Name': item.css('h2::text').get(),
                    'URL' : item.xpath('a/@href').get()
                }
            # yield {
            #    'Stock': 1 if item.css('p.stock.out-of-stock').get() is None else 0,
            #    'Name': item.css('h2::text').get(),
            # }

        next_button = response.css('span.pager-text.right')
        if next_button.get() is not None:
            next_page = next_button.xpath('../@href').get()
            yield response.follow(next_page, self.parse)
        else:
            yield {}


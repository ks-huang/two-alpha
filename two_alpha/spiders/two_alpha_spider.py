import logging
import random
import scrapy

from itertools import cycle
from scrapy.loader import ItemLoader
from scrapy.http import Request
from two_alpha.items import ReloadingItem

logger = logging.getLogger(__name__)

class TwoAlphaSpider(scrapy.Spider):
    def start_requests(self):
        addrs = self.settings['BIND_ADDRESSES']
        random.shuffle(addrs)
        addrs_cycle = cycle(addrs)
        for url in self.start_urls:
            ip = next(addrs_cycle)
            logger.info('bind ip: {}.'.format(ip))
            yield Request(url, dont_filter=True, meta={'bindaddress': (ip, 0)})


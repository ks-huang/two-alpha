import os
import random
from scrapy.cmdline import execute
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from twisted.internet import reactor

from two_alpha.spiders.powder_valley import PowderValleySpider



def crawl_job():
    """
    Job to start spiders.
    Return Deferred, which will execute after crawl has completed.
    """
    
    settings = get_project_settings()
    settings['FEEDS'] = { 'result.csv': {'format' : 'csv'} }
    configure_logging()
    runner = CrawlerRunner(settings)
    return runner.crawl(PowderValleySpider)

def schedule_next_crawl(null, sleep_time):
    """
    Schedule the next crawl
    """
    print('sleep for: {} secs'.format(sleep_time))
    reactor.callLater(sleep_time, crawl)

def crawl():
    """
    A "recursive" function that schedules a crawl 30 seconds after
    each successful crawl.
    """
    # crawl_job() returns a Deferred
    d = crawl_job()
    # call schedule_next_crawl(<scrapy response>, n) after crawl job is complete
    d.addCallback(schedule_next_crawl, random.randint(61, 121))
    d.addErrback(catch_error)

def catch_error(failure):
    print(failure.value)

if __name__=="__main__":
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    crawl()
    reactor.run()

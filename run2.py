import datetime
from datetime import datetime as dt, date
import logging
import os
import pytz
import random
from scrapy.cmdline import execute
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
import time
from twisted.internet import reactor

from two_alpha.spiders.bcm import BcmSpider
from two_alpha.spiders.powder_valley import PowderValleySpider


m1, s1 = random.randint(0, 59), random.randint(0, 59)
m2, s2 = random.randint(0, 59), random.randint(0, 59)

logger = logging.getLogger(__name__)

def crawl_job():
    """
    Job to start spiders.
    Return Deferred, which will execute after crawl has completed.
    """
    
    settings = get_project_settings()
    settings['FEEDS'] = { 'result.csv': {'format' : 'csv'} }
    configure_logging()
    runner = CrawlerRunner(settings)
    runner.crawl(BcmSpider)
    runner.crawl(PowderValleySpider)
    return runner.join()

def schedule_next_crawl(null, sleep_time):
    """
    Schedule the next crawl
    """
    logger.info('sleep for: {} secs'.format(sleep_time))
    reactor.callLater(sleep_time, crawl)

def crawl():
    """
    A "recursive" function that schedules a crawl 30 seconds after
    each successful crawl.
    """

    global m1, s1, m2, s2
    est = pytz.timezone('US/Eastern')
    t1, cur, t2 = datetime.time(8, m1, s1),  dt.utcnow().replace(tzinfo=pytz.utc).astimezone(est).time(),  datetime.time(20, m2, s2)
    if t1 < cur < t2:
        # crawl_job() returns a Deferred
        d = crawl_job()

        # call schedule_next_crawl(<scrapy response>, n) after crawl job is complete
        d.addCallback(schedule_next_crawl, random.randint(61, 121))
        d.addErrback(catch_error)
    else:
        diff = dt.combine(date.min, t1) - dt.combine(date.min, cur)
        msg = 'Blackout hour: cur: {} not in [{} {}], sleep {} seconds'.format(cur, t1, t2, diff)
        print(msg)
        logger.info(msg)
        # reactor.callFromThread(reactor.stop)
        time.sleep(diff.total_seconds())

        # randomize the start, end time
        m1, s1 = random.randint(0, 59), random.randint(0, 59)
        m2, s2 = random.randint(0, 59), random.randint(0, 59)


def catch_error(failure):
    print(failure.value)

if __name__=="__main__":
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    crawl()
    reactor.run()

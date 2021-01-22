import datetime
from datetime import datetime as dt, date, timedelta
import logging
import os
import pytz
import random
from scrapy.cmdline import execute
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from twisted.internet import reactor

from two_alpha.spiders.bcm import BcmSpider
from two_alpha.spiders.powder_valley import PowderValleySpider

START_HOUR = 7
END_HOUR = 23
t1 = datetime.time(START_HOUR, random.randint(0, 59), random.randint(0, 59))
t2 = datetime.time(END_HOUR, random.randint(0, 59), random.randint(0, 59))
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

    global t1, t2
    est = pytz.timezone('US/Eastern')
    cur = dt.utcnow().replace(tzinfo=pytz.utc).astimezone(est).time()

    if t1 < cur < t2:
        # crawl_job() returns a Deferred
        d = crawl_job()

        # call schedule_next_crawl(<scrapy response>, n) after crawl job is complete
        d.addCallback(schedule_next_crawl, random.randint(61, 121))
        d.addErrback(catch_error)
    else:
        # Re-randomize the start/end time
        t1 = datetime.time(START_HOUR, random.randint(0, 59), random.randint(0, 59))
        t2 = datetime.time(END_HOUR, random.randint(0, 59), random.randint(0, 59))
        diff = dt.combine(date.min, t1) - dt.combine(date.min, cur)

        if cur >= t2:
            diff += timedelta(days = 1)
        else:
            diff = max(timedelta(0), diff)

        msg = 'Blackout hour: cur: {} not in [{} {}], sleep {} seconds'.format(cur, t1, t2, diff)
        print(msg)
        logger.info(msg)
        # reactor.callFromThread(reactor.stop)
        reactor.callLater(diff.total_seconds(), crawl)


def catch_error(failure):
    print(failure.value)

if __name__=="__main__":
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    crawl()
    reactor.run()

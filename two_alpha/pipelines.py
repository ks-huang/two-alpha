# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from email.message import EmailMessage
from itemadapter import ItemAdapter
import json
import logging
import os
import smtplib
import time

logger = logging.getLogger(__name__)

class TwoAlphaPipeline:
    GMAIL_ACCOUNT = 'fogworld2019@gmail.com'
    GMAIL_PASSWORD = 'marath0n'

    def __init__(self):
        self.snapshots = {}
        self.lastSnapshots = {}
        self.snapshot_file_path = '/tmp/scrapy'
        self.snapshot_file_prefix = 'snapshot-'
        self.snapshot_file_name = self.snapshot_file_prefix + '{}.json'

        if not os.path.exists(self.snapshot_file_path):
            os.makedirs(self.snapshot_file_path)

    def send_notification(self, email, content):
        # Establish a secure session with gmail's outgoing SMTP server using your gmail account
        server = smtplib.SMTP( "smtp.gmail.com", 587 )
        server.starttls()
        server.login(self.GMAIL_ACCOUNT, self.GMAIL_PASSWORD)

        # Send text message through SMS gateway of destination number
        msg = EmailMessage()
        msg.set_content(content)
        msg['To'] = email
        msg['From'] = self.GMAIL_ACCOUNT
        server.send_message(msg)

    def open_spider(self, spider):
        cname = spider.__class__.__name__
        self.snapshots[cname] = {}
        try:
            with open(os.path.join(self.snapshot_file_path, self.snapshot_file_name.format(cname)), 'r') as f:
                self.lastSnapshots[cname] = json.load(f)
                logger.info("Last snapshot: {}".format(len(self.lastSnapshots[cname])))
        except IOError:
            self.lastSnapshots[cname] = {}

    def close_spider(self, spider):
        # update snapshot
        cname = spider.__class__.__name__
        snapshot = self.snapshots[cname]
        data = json.dumps(snapshot)
        with open(os.path.join(self.snapshot_file_path, self.snapshot_file_name.format(cname)), 'w') as outfile:
            outfile.write(data)

        # dump product added
        lastSnapshot = self.lastSnapshots[cname]
        diff = { k : snapshot[k] for k, _ in set(snapshot.items()) - set(lastSnapshot.items()) }
        logger.info("Newly added...")
        logger.info(diff)
        if diff:
            msg = ''.join([p + ': ' + u + '\n' for p, u in diff.items()])
            email = '6467632336@vzwpix.com'
            self.send_notification(email, msg)
            stamped_file_path = os.path.join(self.snapshot_file_path, self.snapshot_file_name.format(cname + '-' + time.strftime("%Y%m%d-%H%M%S")))
            with open(stamped_file_path, 'w') as outfile:
                outfile.write(data)

        # dump product removed
        diff = { k : lastSnapshot[k] for k in set(lastSnapshot) - set(snapshot) }
        logger.info("Last: {}, Curr: {}, Just gone...".format(len(lastSnapshot), len(snapshot)))
        logger.info(diff)

    def process_item(self, item, spider):
        prod = item['product_name']
        url = item['url']
        cname = spider.__class__.__name__
        snapshot = self.snapshots[cname]

        snapshot[prod] = url
        return item

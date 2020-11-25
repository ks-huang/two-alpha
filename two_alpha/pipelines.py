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
    snapshot = {}
    GMAIL_ACCOUNT = 'fogworld2019@gmail.com'
    GMAIL_PASSWORD = 'marath0n'

    def __init__(self):
        self.snapshot_file_path = '/tmp/scrapy'
        self.snapshot_file_prefix = 'snapshot-'
        self.snapshot_file_name = self.snapshot_file_prefix + self.__class__.__name__ + '.json'

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
        try:
            with open(os.path.join(self.snapshot_file_path, self.snapshot_file_name), 'r') as f:
                self.lastSnapshot = json.load(f)
        except IOError:
            self.lastSnapshot = {}

    def close_spider(self, spider):
        # update snapshot
        data = json.dumps(self.snapshot)
        with open(os.path.join(self.snapshot_file_path, self.snapshot_file_name), 'w') as outfile:
            outfile.write(data)

        # dump product added
        diff = { k : self.snapshot[k] for k, _ in set(self.snapshot.items()) - set(self.lastSnapshot.items()) }
        logger.info("Newly added...")
        logger.info(diff)
        if diff:
            msg = ''.join([p + ': ' + u + '\n' for p, u in diff.items()])
            email = '6467632336@vzwpix.com'
            self.send_notification(email, msg)
            stamped_file_path = os.path.join(self.snapshot_file_path, self.snapshot_file_prefix + time.strftime("%Y%m%d-%H%M%S") + '.json')
            with open(stamped_file_path, 'w') as outfile:
                outfile.write(data)

        # dump product removed
        diff = { k : self.lastSnapshot[k] for k in set(self.lastSnapshot) - set(self.snapshot) }
        logger.info("Just gone...")
        logger.info(diff)

    def process_item(self, item, spider):
        prod = item['product_name']
        url = item['url']

        self.snapshot[prod] = url
        return item

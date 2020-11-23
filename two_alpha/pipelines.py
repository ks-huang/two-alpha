# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json
import logging
import os
import time

class TwoAlphaPipeline:
    snapshot = {}

    def __init__(self):
        self.snapshot_file_path = '/tmp/scapy'
        self.snapshot_file_prefix = 'snapshot-'
        self.snapshot_file_name = self.snapshot_file_prefix + self.__class__.__name__ + '.json'

        if not os.path.exists(self.snapshot_file_path):
            os.makedirs(self.snapshot_file_path)

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
        logging.info("Newly added...")
        logging.info(diff)
        if diff:
            stamped_file_path = os.path.join(self.snapshot_file_path, self.snapshot_file_prefix + time.strftime("%Y%m%d-%H%M%S") + '.json')
            with open(stamped_file_path, 'w') as outfile:
                outfile.write(data)

        # dump product removed
        diff = { k : self.lastSnapshot[k] for k in set(self.lastSnapshot) - set(self.snapshot) }
        logging.info("Just gone...")
        logging.info(diff)

    def process_item(self, item, spider):
        prod = item['product_name']
        url = item['url']

        self.snapshot[prod] = url
        return item

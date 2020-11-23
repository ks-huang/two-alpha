# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json
import logging

class TwoAlphaPipeline:
    snapshot = {}

    def __init__(self):
        self.snapshot_file_path = '/tmp/snapshot-' + self.__class__.__name__ + '.json'

    def open_spider(self, spider):
        try:
            with open(self.snapshot_file_path, 'r') as f:
                self.lastSnapshot = json.load(f)
        except IOError:
            self.lastSnapshot = {}

    def close_spider(self, spider):
        # dump product added
        diff = { k : self.snapshot[k] for k, _ in set(self.snapshot.items()) - set(self.lastSnapshot.items()) }
        logging.info("Newly added...")
        logging.info(diff)

        # dump product removed
        diff = { k : self.lastSnapshot[k] for k in set(self.lastSnapshot) - set(self.snapshot) }
        logging.info("Just gone...")
        logging.info(diff)

        # update snapshot
        data = json.dumps(self.snapshot)
        with open(self.snapshot_file_path, 'w') as outfile:
            outfile.write(data)

    def process_item(self, item, spider):
        prod = item['product_name']
        url = item['url']

        self.snapshot[prod] = url
        return item

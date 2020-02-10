# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import re
from scrapy.exceptions import DropItem
from scrapy.exceptions import CloseSpider
from lossless.items import DownloadLink
from scrapy.exporters import CsvItemExporter

class DuplicatesPipeline(object):

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):

        #print("AT DUPLICATES PIPELINE PROCESSITEM POINT")
        #print(item)
        thetype = item['type']
        duplicatefound = 0
        f = open('{}.csv'.format(thetype), 'rb')

        for line in f:
            if re.search(item['url'].encode(),line):
                #print("FOUND DUPLICATE %s" % str(item['url']))
                duplicatefound = 1

        if duplicatefound == 1:

            if (spider.update == "1" and spider.page == "recente") 
            or (spider.update == "1" and spider.page == "cereri"):

                raise DropItem('item dropped, continuing. because update = 1'
                                'and not main (duplicate being actually '
                                'repost of NEW content, checking next post in '
                                'topic on page spider.page')

                print("DUPLICATE NOT FOUND. SENDING TO 2nd PIPELINE %s" 
                      % str(item['url']))

                self.ids_seen.add(item['url'])
                return item

            else if (spider.update == "1" and spider.page == "main"):

                raise DropItem('item dropped. because crawling subforum '
                               'page 1, already uptodate. CLOSING!')

                spider.close_maincrawler = True

            else if (spider.update == "0" and spider.page == "main"):

                raise DropItem('duplicate found but not updating, can delete '
                               'duplicate and continue doing werk ;not very '
                               'probable')

            else if (spider.update == "0" and spider.page == "recente" 
                 or (spider.update == "0" and spider.page == "cereri"):

                raise DropItem('duplicate found but not updating, can delete '
                                duplicate and continue doing werk')

        else if duplicatefound == 0:

            print("url %s is not duplicate, sending to 2nd pipeline" 
                  % str(item['url']))
            print("DUPLICATE NOT FOUND. SENDING TO 2nd PIPELINE %s" 
                  % str(item['url']))

            self.ids_seen.add(item['url'])
            return item


class PerTypeCsvExportPipeline(object):

    def open_spider(self, spider):
        self.type_to_exporter = {}

    def close_spider(self, spider):
        for exporter in self.type_to_exporter.values():
            exporter.finish_exporting()

    def _exporter_for_item(self, item):
        #print("item at exporter_for_item")
        #print(item)
        thetype = item['type']
        if thetype not in self.type_to_exporter:
            f = open('{}.csv'.format(thetype), 'a+b')
            exporter = CsvItemExporter(f,False)
            exporter.encoding = {'utf-8'}
            exporter.fields_to_export = {'url'}
            print("WRITING LINK %s to FILE %s.csv" % item['url'], thetype)
            exporter.start_exporting()
            self.type_to_exporter[thetype] = exporter
        return self.type_to_exporter[thetype]

    def process_item(self, item, spider):
        #print("item at process_item")
        #print(item)
        exporter = self._exporter_for_item(item)
        exporter.export_item(item)
        return item

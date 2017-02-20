# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from jobs.items import COMPANY_FIELDS, JOB_FIELDS, AGGREGATOR_JOB_FIELDS
from jobs.idspider import IdSpider
import csv, json, os

class JobsPipeline(object):
    FIELDS = JOB_FIELDS
    
    def open_spider(self, spider):
        self.filename = 'data/' + spider.name + '.csv'
        existed = os.path.exists(self.filename)
        self.ids_file = None
        if isinstance(spider, IdSpider):
            self.file = open(self.filename, 'ab')
            self.ids_file = open('data/' + spider.name + '_ids', 'ab')
        else:
            self.file = open(self.filename, 'wb')
            existed = False
        self.csv_writer = csv.writer(self.file, delimiter = ',', quotechar = '"',
            quoting = csv.QUOTE_MINIMAL)
        if not existed:
            self.csv_writer.writerow(self.FIELDS)
    
    def close_spider(self, spider):
        self.file.close()
        if self.ids_file:
            self.ids_file.close()
    
    def process_item(self, item, spider):
        item['listings'] = json.dumps(item['listings'])
        self.csv_writer.writerow([uc.encode('utf-8') if isinstance(uc, unicode) else uc\
                for uc in [item.get(key, u'') for key in self.FIELDS]])
        if self.ids_file:
            self.ids_file.write(str(item['job_id']) + '\n')
        return item

class AggregatorJobsPipeline(JobsPipeline):
    FIELDS = AGGREGATOR_JOB_FIELDS

class CompaniesPipeline(object):
    def __init__(self):
        self.filename = 'data/companies_fortune500.csv'
        self.fields = [x[2] for x in COMPANY_FIELDS]
    
    def open_spider(self, spider):
        self.file = open(self.filename, 'wb')
        self.csv_writer = csv.writer(self.file, delimiter = ',', quotechar = '"',
            quoting=csv.QUOTE_MINIMAL)
        self.csv_writer.writerow(self.fields)
    
    def close_spider(self, spider):
        self.file.close()
    
    def process_item(self, item, spider):
        self.csv_writer.writerow([uc.encode('utf-8') if isinstance(uc, unicode) else uc\
                for uc in [item.get(elem, u'') for elem in self.fields]])
        return item

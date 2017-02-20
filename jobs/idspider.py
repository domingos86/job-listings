# -*- coding: utf-8 -*-
from scrapy import Spider

'''
Template Spider. Not meant to be used unless subclassed
'''
class IdSpider(Spider):
    def __init__(self):
        self.ids = set()
        try:
            with open('data/' + self.name + '_ids', 'rb') as f:
                for line in f:
                    self.ids.add(line.strip())
        except:
            pass
        super(Spider, self).__init__()

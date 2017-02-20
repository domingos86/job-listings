# -*- coding: utf-8 -*-
from scrapy import Spider
from jobs.items import COMPANY_FIELDS
import json

class ListCompaniesSpider(Spider):
    name = "list_companies"
    allowed_domains = ["fortune.com"]
    start_urls = ['http://fortune.com/api/v2/list/1666518/expand/item/ranking/asc/'\
        + str(i) + '/100' for i in range(0, 500, 100)]
    
    custom_settings = {
        'ITEM_PIPELINES': {
            'jobs.pipelines.CompaniesPipeline': 100
        }
    }

    def parse(self, response):
        data = json.loads(response.body)
        for item in data.get('list-items', []):
            try:
                outDict = {}
                for func, x, y in COMPANY_FIELDS:
                    outDict[y] = func(item, x)
                yield outDict
            except Exception as excpt:
                self.logger.error('Unable to parse company\'s json: '\
                    + str(item) + '\n' + str(excpt))

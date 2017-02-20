# -*- coding: utf-8 -*-
from scrapy import Request
from jobs.idspider import IdSpider
from jobs.items import AggregatorJobPosting
import re, datetime, json, urllib

get_list_url = lambda page, query: 'http://service.dice.com/api/rest/jobsearch/v1/simple.json?pgcnt=50&page=' +\
        str(page) + '&text=' + query + '&country=us'

class GetJobsSpider(IdSpider):
    name = "dice"
    allowed_domains = ["dice.com"]
    query_terms = [urllib.quote_plus(q) for q in ["data scientist", "data engineer", "business analyst"]]
    download_delay = 1
    
    def start_requests(self):
        return [Request(get_list_url(1, query_term),
                    callback = self.parse_list) for query_term in self.query_terms]
        
    custom_settings = {
        'ITEM_PIPELINES': {
            'jobs.pipelines.AggregatorJobsPipeline': 100
        }#,'ROBOTSTXT_OBEY': False
    }

    def parse_list(self, response):
        list_json = json.loads(response.body)
        for posting in list_json.get('resultItemList', []):
            try:
                match = re.search(r'/result/(.+)\?src', posting['detailUrl'])
                job_id = match.group(1)
                if job_id in self.ids:
                    self.logger.debug('Detected posting already stored, with id ' + job_id + '. Skipping...')
                    continue
                # Make sure we do not scrape the same post during the same session, as we might be dealing with multiple search queries
                self.ids.add(job_id)
                yield Request(posting['detailUrl'].replace('http://www.dice.com/job/result/',
                            'https://www.dice.com/jobs/detail/'), callback=self.parse_posting,
                        meta = {'job_meta': posting, 'job_id': job_id})
            except Exception as excpt:
                self.logger.error('Unable to parse Dice\'s: '\
                    + str(posting) + '\n' + str(excpt))
        if 'nextUrl' in list_json:
            yield Request(response.urljoin(list_json['nextUrl']),
                    callback = self.parse_list)
    
    def parse_posting(self, response):
        try:
            job_meta = response.meta['job_meta']
            job_id = response.meta['job_id']
            title = job_meta.get(u'jobTitle', '')
            location = job_meta.get(u'location', '')
            date_posted = job_meta.get(u'date', '')
            if len(date_posted) > 0:
                # 2017-02-09
                date_posted = datetime.datetime.strptime(date_posted, '%Y-%m-%d').date()
            company = job_meta.get(u'company', '')
            url = response.url
            role_description = '\n'.join(response.xpath('//div[@id="jobdescSec"]//text()').extract())
            
            posting = AggregatorJobPosting()
            posting['job_id'] = job_id
            posting['title'] = title.strip()
            posting['company'] = company.strip()
            posting['location'] = location.strip()
            posting['date_posted'] = date_posted
            posting['time_scraped'] = datetime.datetime.now()
            posting['url'] = url
            posting['role_description'] = role_description.strip()
            posting['listings'] = []
            yield posting
        except Exception as excpt:
            self.logger.error('Unable to parse Dice\'s: '\
                + response.body + '\n' + str(excpt))

# -*- coding: utf-8 -*-
from scrapy import Request
from jobs.idspider import IdSpider
from jobs.items import AggregatorJobPosting
import re, datetime, json, requests, urllib

publisher_key = ### Insert your key!!

get_list_url = lambda start, user_ip, query: 'http://api.indeed.com/ads/apisearch?sort=date&co=us&format=json&highlight=0&publisher=' +\
        publisher_key + '&q=' + query + '&start=' + str(start) + '&limit=25&v=2&userip=' + user_ip +\
        '&useragent=Mozilla%2F5.0+%28X11%3B+Ubuntu%3B+Linux+x86_64%3B+rv%3A50.0%29+Gecko%2F20100101+Firefox%2F50.0'

class GetJobsSpider(IdSpider):
    name = "indeed"
    allowed_domains = ["indeed.com"]
    query_terms = [urllib.quote_plus(q) for q in ["data scientist", "data engineer", "business analyst"]]
    
    def start_requests(self):
        self.user_ip = requests.get('https://api.ipify.org').text
        return [Request(get_list_url(0, self.user_ip, query_term),
                    callback = self.parse_list) for query_term in self.query_terms]
        
    custom_settings = {
        'ITEM_PIPELINES': {
            'jobs.pipelines.AggregatorJobsPipeline': 100
        },
        'ROBOTSTXT_OBEY': False
    }

    def parse_list(self, response):
        list_json = json.loads(response.body)
        for posting in list_json.get('results', []):
            try:
                job_id = posting[u'jobkey']
                if job_id in self.ids:
                    self.logger.debug('Detected posting already stored, with id ' + job_id + '. Skipping...')
                    continue
                # Make sure we do not scrape the same post during the same session, as we might be dealing with multiple search queries
                self.ids.add(job_id)
                yield Request(posting[u'url'], callback=self.parse_posting,
                        meta = {'job_meta': posting})
            except Exception as excpt:
                self.logger.error('Unable to parse Indeed\'s: '\
                    + str(posting) + '\n' + str(excpt))
        if list_json.get(u'end', 10000000) < list_json.get(u'totalResults', 0):
            yield Request(get_list_url(list_json[u'end'], self.user_ip, list_json[u'query']),
                    callback = self.parse_list)
    
    def parse_posting(self, response):
        try:
            job_meta = response.meta['job_meta']
            job_id = job_meta[u'jobkey']
            title = job_meta.get(u'jobtitle', '')
            location = job_meta.get(u'formattedLocationFull', job_meta.get(u'formattedLocation', job_meta.get(u'city', '')))
            date_posted = job_meta.get(u'date', '')
            if len(date_posted) > 0:
                # Wed, 25 Jan 2017 17:41:20 GMT
                found_date = re.search(r'^\w+,\s(\d{1,2}\s+\w{3,3}\s+\d{2,4}),?\s+', date_posted)
                if found_date:
                    date_posted = datetime.datetime.strptime(found_date.group(1), '%d %b %Y').date()
            company = job_meta.get(u'company', '')
            url = job_meta[u'url']
            content = response.xpath('//table[@id="job-content"]/tr[1]/td[1]/table[1]/tr[1]/td[1]')
            original_url = content.xpath('.//a[contains(@class, "view_job_link")]/@href').extract_first()
            if original_url:
                original_url = response.urljoin(original_url)
            content = content.xpath('./span[@id="job_summary"]')
            role_description = '\n'.join(content.xpath('.//text()').extract())
            
            posting = AggregatorJobPosting()
            posting['job_id'] = job_id
            posting['title'] = title.strip()
            posting['company'] = company
            posting['location'] = location.strip()
            posting['date_posted'] = date_posted
            posting['time_scraped'] = datetime.datetime.now()
            posting['url'] = url
            posting['role_description'] = role_description.strip()
            posting['original_url'] = original_url
            posting['listings'] = []
            yield posting
        except Exception as excpt:
            self.logger.error('Unable to parse Indeed\'s: '\
                + response.body + '\n' + str(excpt))

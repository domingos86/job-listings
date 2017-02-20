# -*- coding: utf-8 -*-
from scrapy import Spider, Request, Selector
from jobs.items import JobPosting
import re, datetime, json, urllib

amazon_headers = {
    'Host': 'www.amazon.jobs',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
    'DNT': '1',
    'Connection': 'keep-alive'
}

get_list_url = lambda offset, query: 'https://www.amazon.jobs/en/search?base_query=' +\
        query + '&sort=relevant&result_limit=100&offset=' + str(offset)

class GetJobsSpider(Spider):
    name = "amazon"
    allowed_domains = ["amazon.jobs"]
    query_terms = [urllib.quote_plus(q) for q in ["data scientist", "data engineer", "business analyst"]]
    
    def start_requests(self):
        return [Request(get_list_url(0, query_term),
                    meta = {'offset': 0, 'query_term': query_term},
                    headers = amazon_headers, callback = self.parse_list)
                for query_term in self.query_terms]
        
    custom_settings = {
        'ITEM_PIPELINES': {
            'jobs.pipelines.JobsPipeline': 100
        }
    }
    
    def __init__(self):
        self.ids = set()
        super(Spider, self).__init__()

    def parse_list(self, response):
        json_list = json.loads(response.body)
        count = int(json_list.get('hits', 0))
        self.logger.debug('Got %d results.' % count)
        offset = response.meta['offset']
        query_term = response.meta['query_term']
        for job_json in json_list.get('jobs', []):
            try:
                country = job_json.get('country_code', None)
                if country is None:
                    country = job_json.get('location', '')
                if re.match('US.*', country) is None:
                    self.logger.debug('Country is not USA: "' + country + '". Skipping...')
                    continue
                job_id = job_json['id']
                if job_id in self.ids:
                    continue
                self.ids.add(job_id)
                title = job_json['title']
                location = job_json.get('location', '')
                date_posted = job_json.get(u'posted_date', '')
                if len(date_posted) > 0:
                    try:
                        date_posted = datetime.datetime.strptime(date_posted, '%B %d, %Y').date()
                    except:
                        date_posted = datetime.datetime.strptime(date_posted, '%B  %d, %Y').date()
                department = job_json.get('job_category', '')
                role_description = job_json.get(u'description', '')
                url = response.urljoin(job_json.get(u'job_path', '/en/jobs/' + job_json.get(u'id_icims', '')))
                listings = []
                for key, value in [(u'basic_qualifications', 'Basic Qualifications'),
                        (u'preferred_qualifications', 'Preferred Qualifications')]:
                    if key not in job_json:
                        continue
                    this_listing = {}
                    this_listing['type'] = value
                    this_listing['elements'] = [x for x in [elem.replace(u'\u2022', '').strip() for elem in re.split('<br/>\\s*\u2022', job_json[key].strip())] if len(x) > 0]
                    listings.append(this_listing)
                
                posting = JobPosting()
                posting['job_id'] = job_id
                posting['title'] = title.strip()
                posting['department'] = department.strip()
                posting['location'] = location.strip()
                posting['date_posted'] = date_posted
                posting['time_scraped'] = datetime.datetime.now()
                posting['url'] = url
                posting['role_description'] = role_description.strip()
                posting['listings'] = listings
                yield posting
            except Exception as excpt:
                self.logger.error('Unable to parse Amazons\'s: '\
                    + str(job_json) + '\n' + str(excpt))
        if offset + 100 < count:
            yield Request(get_list_url(offset + 100, query_term), meta = {'offset': offset + 100, 'query_term': query_term},
                    headers = amazon_headers, callback = self.parse_list)
        else:
            self.logger.debug('Not submitting any more requests. offset = %d, count = %d' %(offset, count))

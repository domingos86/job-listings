# -*- coding: utf-8 -*-
from scrapy import Spider, FormRequest, Selector
from jobs.idspider import IdSpider
from jobs.items import JobPosting
import re, datetime, json
    
def get_list_form_data(page_number, query):
    return {'searchRequestJson': '{"searchString":"' + query + '","jobType":"1",' +\
                    '"sortOrder":"","filters":{"locations":{"location":[{"type":"0","code":"USA"}]}},' +\
                    '"pageNumber":"' + str(page_number) + '"}',
            'csrfToken': 'null', 'clientOffset': '-300'}

listing_converter = {u'additionalRequirements': 'Additional Requirements',
  u'description': 'Description', u'educationDetails': 'Education',
  u'keyQualifications': 'Qualifications',
  u'preferredQualifications': 'Preferred Qualifications'}

class GetJobsSpider(IdSpider):
    name = "apple"
    allowed_domains = ["jobs.apple.com"]
    query_terms = ["data scientist", "data engineer", "business analyst"]
    
    def start_requests(self):
        return [FormRequest('https://jobs.apple.com/us/search/search-result',
                    formdata = get_list_form_data(0, query_term), callback = self.parse_list,
                    meta = {'page_number': 0, 'query_term': query_term})
                for query_term in self.query_terms]
        
    custom_settings = {
        'ITEM_PIPELINES': {
            'jobs.pipelines.JobsPipeline': 100
        }
    }

    def parse_list(self, response):
        count = int(response.xpath('/html/body/result/count/text()').extract_first())
        pagenum = response.meta['page_number']
        query_term = response.meta['query_term']
        for posting in response.xpath('/html/body/result/requisition'):
            try:
                job_id = posting.xpath('./jobid/text()').extract_first()
                if job_id in self.ids:
                    self.logger.debug('Detected posting already stored, with id ' + job_id + '. Skipping...')
                    continue
                # Make sure we do not scrape the same post during the same session, as we might be dealing with multiple search queries
                self.ids.add(job_id)
                yield FormRequest('https://jobs.apple.com/us/requisition/detail.json',
                        formdata = {'requisitionId': job_id, 'reqType': 'REQ', 'clientOffset': '-300'},
                        callback=self.parse_posting,
                        meta = {'job_function': posting.xpath('./jobfunction/text()').extract_first()})
            except Exception as excpt:
                self.logger.error('Unable to parse Apple\'s: '\
                    + str(posting) + '\n' + str(excpt))
        if (count - 1) / 20 > pagenum:
            yield FormRequest('https://jobs.apple.com/us/search/search-result',
                    formdata = get_list_form_data(pagenum + 1, query_term), callback = self.parse_list,
                    meta = {'page_number': pagenum + 1, 'query_term': query_term})
    
    def parse_posting(self, response):
        try:
            job_json = json.loads(response.body)
            req_info = job_json.get(u'requisitionInfo', {})
            job_id = req_info.get(u'formId', 0)
            title = req_info.get(u'postingTitle', '')
            if len(title) == 0 or job_id == 0:
                self.logger.error('job title/id not found (perhaps "requisitionInfo" key missing)\n' + response.body)
                return
            location = req_info.get(u'locationName', '')
            state = req_info.get(u'stateAbbr', '')
            if len(state) > 0:
                location = location + ', ' + state
            date_posted = req_info.get(u'reqOpenDt', '')
            if len(date_posted) > 0:
                date_posted = datetime.datetime.strptime(date_posted, '%d-%b-%Y').date()
            role_description = job_json.get(u'jobComments', '')
            listings = []
            for key, value in job_json.get(u'reqTextFields', {}).iteritems():
                key = listing_converter.get(key, '')
                if len(key) == 0 or not isinstance(value, basestring):
                    continue
                this_listing = {}
                this_listing['type'] = key
                this_listing['elements'] = [x for x in [elem.strip() for elem in value.strip().split('\n')] if len(x) > 0]
                listings.append(this_listing)
            
            posting = JobPosting()
            posting['job_id'] = job_id
            posting['title'] = title.strip()
            posting['department'] = response.meta['job_function'].strip()
            posting['location'] = location.strip()
            posting['date_posted'] = date_posted
            posting['time_scraped'] = datetime.datetime.now()
            posting['url'] = 'https://jobs.apple.com/us/search#&ss=' + str(job_id)
            posting['role_description'] = role_description.strip()
            posting['listings'] = listings
            yield posting
        except Exception as excpt:
            self.logger.error('Unable to parse apple\'s: '\
                + response.body + '\n' + str(excpt))

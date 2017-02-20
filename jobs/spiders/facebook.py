# -*- coding: utf-8 -*-
from scrapy import Spider, Request, Selector
from jobs.idspider import IdSpider
from jobs.items import JobPosting
import re, datetime

# Facebook uses ids to tell whether a particular item was already scraped or not
# also, we should be filtering by location

class GetJobsSpider(IdSpider):
    name = "facebook"
    allowed_domains = ["facebook.com"]
    start_urls = ['https://www.facebook.com/careers/search/?q=' + query_term
                    for query_term in ['data%20scientist', 'data%20engineer', 'business%20analyst']]
    
    custom_settings = {
        'ITEM_PIPELINES': {
            'jobs.pipelines.JobsPipeline': 100
        },
        'ROBOTSTXT_OBEY': False
    }

    def parse(self, response):
        for posting in response.xpath('//div[@class="_3k6i"]'):
            try:
                link = posting.xpath('.//a[contains(@class, "_5144")]/@href').extract_first()
                #title = ''.join(posting.xpath('.//a[contains(@class, "_5144")]//text()').extract())
                #topic = ''.join(posting.xpath('.//div[contains(@class, "_3k6l")]//text()').extract())
                location = ''.join(posting.xpath('.//div[contains(@class, "_3k6n")]//text()').extract())
                job_id = re.search('/careers/jobs/([^/]+)/', link).group(1)
                if job_id in self.ids:
                    self.logger.debug('Detected posting already stored, with id ' + job_id + '. Skipping...')
                    continue
                if not re.search(', [A-Z][A-Z]', location):
                    self.logger.debug('Location doesn\'t seem to be in the US or Canada: "' + location + '". Skipping...')
                    continue
                # Make sure we do not scrape the same post during the same session, as we might be dealing with multiple search queries
                self.ids.add(job_id)
                yield Request(response.urljoin(link), callback=self.parse_posting)
            except Exception as excpt:
                self.logger.error('Unable to parse facebook\'s: '\
                    + str(posting) + '\n' + str(excpt))
    
    def parse_posting(self, response):
        try:
            topic = ''.join(response.xpath('//div[contains(@class, "_35i2")]//text()').extract())
            content = response.xpath('//div[@class="_4ycv"]')
            title = ''.join(content.xpath('.//*[contains(@class, "_4ycw")]//text()').extract())
            location = ''.join(content.xpath('.//div[contains(@class, "_4ycx")]//text()').extract())
            location = '|'.join(re.search(r'^\((.+)\)$', location).group(1).split(' - '))
            company_intro = ''.join(content.xpath('div[2]//text()').extract())
            description = content.xpath('div[3]')
            role_description = ''.join(description.xpath('self::div[@class != "_wrz"]//text()').extract())
            listings = []
            for listing in content.xpath('.//div[@class="_wrz"]'):
                this_listing = {}
                this_listing['type'] = ''.join(listing.xpath('.//h4//text()').extract()).strip()
                this_listing['elements'] = [''.join(list_elem.xpath('.//text()').extract()).strip()
                        for list_elem in listing.xpath('.//ul/li')]
                listings.append(this_listing)
            job_id = content.xpath('.//a[@id="u_0_d"]/@href').extract_first()
            job_id = re.search(r'^/careers/resume\?(?:.*&)?req=([^&]+)(?:&.*)?$', job_id).group(1)
            
            posting = JobPosting()
            posting['job_id'] = job_id
            posting['title'] = title.strip()
            posting['department'] = topic.strip()
            posting['location'] = location.strip()
            posting['time_scraped'] = datetime.datetime.now()
            posting['url'] = response.url
            posting['company_intro'] = company_intro.strip()
            posting['role_description'] = role_description.strip()
            posting['listings'] = listings
            yield posting
        except Exception as excpt:
            self.logger.error('Unable to parse facebook\'s: '\
                + response.body + '\n' + str(excpt))

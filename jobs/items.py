# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field

#for x in COMPANY_FIELDS, we apply map(x[0], company_json, x[1])
# and it becomes field x[2] in our csv table

'''
def META_MAP(dic, elem):
    print(type(dic))
    print(dic)
    meta = dic.get(u'meta', {})
    print(type(meta))
    return meta.get(elem, u'')
'''

META_MAP = lambda dic, elem: dic.get(u'meta', {}).get(elem,u'')
COMPANY_FIELDS_META = [
    (META_MAP, x, x) for x in [
  u'slug',
  u'fullname',
  
  u'industry',
  u'sector',
  
  u'website',
  u'hqaddr',
  u'hqcity',
  u'hqstate',
  u'hqzip',
  u'hqtel',
  
  u'ranking', #Fortune 500 ranking
  u'newcomer',
  u'prevrank',
  u'yearsonlist', #Years on Fortune 500 List
  
  u'ceo',
  u'ceoforeign',
  u'ceofounder',
  u'ceowoman',
  
  u'employees',
  u'jobgrowth',
  u'jobgrowthnum',
  
  u'linkedin', #As in https://www.linkedin.com/company-beta/2646?pathWildcard=2646
  u'twitter',
  
  u'assets', #Assets ($M)
  
  u'ticker',
  u'mktval', #Market Value -- as of March 31, 2016 ($M)
  u'totshequity', #Total Stockholder Equity ($M)
  
  u'revenues', #Revenues ($M)
  u'revchange', #Revenue Percent Change
  u'eps', #Earnings Per Share ($)
  u'epschange', #EPS % Change (from 2014)
  u'eps10yr', #EPS % Change (10 year annual rate)
  u'eps5yr', #EPS % Change (5 year annual rate)
  
  u'profitable',
  u'profits', #Profits ($M)
  u'prftchange', #Profits Percent Change
  u'prftpctasts', #Profits as % of Assets
  u'prftpctseqty', #Profits as % of Stockholder Equity
  u'prftpctsls', #Profit as % of Revenues
  
  u'totrti', #Total Return to Investors (2015)
  u'totrti5yr', #Total Return to Investors (5 year, annualized)
  u'totrti10yr', #Total Return to Investors (10 year, annualized)
  
  u'100-fastest-growing-companies-rank', #http://beta.fortune.com/100-fastest-growing-companies/
  u'100-fastest-growing-companies-y-n',
  u'best-companies-rank', #http://fortune.com/best-companies/
  u'best-companies-y-n',
  u'change-the-world-rank', #http://fortune.com/change-the-world/
  u'change-the-world-y-n',
  u'global500-rank', #http://fortune.com/global500/
  u'global500-y-n',
  u'worlds-most-admired-companies-rank', #http://fortune.com/worlds-most-admired-companies/
  u'worlds-most-admired-companies-y-n']]

COMPANY_FIELDS_ROOT = [
    (lambda dic, elem: dic.get(elem, u''), x, y) for x, y in [ 
  (u'id', u'fortune_id'),
  (u'title', u'shortname'),#short name
  (u'description', u'description')]]

COMPANY_FIELDS_COMPANIES = [
    (lambda dic, elem: dic.get('companies', [{}])[0].get(elem, u''), x, y) for x, y in [
  (u'link', u'fortune_link'), #link to profile on Fortune
  (u'logo', u'logo')]]

'''
COMPANY_FIELDS_OURS = [(lambda dic, elem: elem, x, y) for x, y in [
  (u'', u'most_recent_post_time'),
  (u'', u'filter_criteria'),
  (u'no', u'has_spider')]]

COMPANY_FIELDS = COMPANY_FIELDS_META[:2] + COMPANY_FIELDS_OURS +\
    COMPANY_FIELDS_ROOT[:2] + COMPANY_FIELDS_META[2:] +\
    COMPANY_FIELDS_COMPANIES + COMPANY_FIELDS_ROOT[2:]
'''
    
COMPANY_FIELDS = COMPANY_FIELDS_META[:2] +\
    COMPANY_FIELDS_ROOT[:2] + COMPANY_FIELDS_META[2:] +\
    COMPANY_FIELDS_COMPANIES + COMPANY_FIELDS_ROOT[2:]

#class CompanyItem(Item):
#    fields_dict = Field() # we have too many fields to be defining them manually

JOB_FIELDS = ['job_id', 'title', 'department', 'location', 'date_posted',
        'time_scraped', 'url', 'company_intro', 'role_description', 'listings']

class JobPosting(Item):
    job_id = Field()
    title = Field()
    department = Field()
    location = Field()
    date_posted = Field()
    time_scraped = Field()
    url = Field()
    company_intro = Field()
    role_description = Field()
    listings = Field()

AGGREGATOR_JOB_FIELDS = JOB_FIELDS[:2] + ['company'] + JOB_FIELDS[2:] + ['original_url']

class AggregatorJobPosting(JobPosting):
    company = Field()
    original_url = Field()

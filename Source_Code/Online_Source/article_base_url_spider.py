import re
from bs4 import BeautifulSoup
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import json


class BaseURLSpider(CrawlSpider):
    '''
    This class is responsible for crawling globe and mail articles urls
    '''
    name = 'BaseURL'
    allowed_domains = ["www.theglobeandmail.com"]

    # seed urls
    url_path = "../../Sample_Resources/Online_Resources/sample_seed_urls.txt"
    start_urls = [line.strip() for line in open(url_path).readlines()]

    # Rules for including and excluding urls
    rules = (
        Rule(LinkExtractor(allow=r'\/opinion\/.*\/article\d+\/$'), callback="parse_articles"),
    )

    def __init__(self, **kwargs):
        '''
        Read user arguments and initialize variables
        :param kwargs: command line input
        :return: None
        '''
        CrawlSpider.__init__(self)

        self.headers = ({'User-Agent': 'Mozilla/5.0',
                         'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                         'X-Requested-With': 'XMLHttpRequest'})
        self.output_path = "../../Sample_Resources/Online_Resources/sample_base_urls.txt"
        self.ids_seen = set()

    def parse_articles(self, response):
        '''
        Crawl more urls and keep original urls that start with "http://www.theglobeandmail.com/opinion/"
        :param response: url response
        :return: None. Print the urls into base urls
        '''
        article_ptn = "http://www.theglobeandmail.com/opinion/(.*?)/article(\d+)/"
        resp_url = response.url
        article_m = re.match(article_ptn, resp_url)
        article_id = ''
        if article_m != None:
            article_id = article_m.group(2)
            if article_id not in self.ids_seen:
                self.ids_seen.add(article_id)

                soup = BeautifulSoup(response.text, 'html.parser')
                content = soup.find('div', {"class":"column-2 gridcol"})
                if content != None:
                    text = content.findAll('p', {"class":''})
                    if len(text) > 0:
                            print('*****Article ID*****', article_id)
                            print('***Article URL***', resp_url)

                            with open(self.output_path, 'a') as out:
                                out.write(resp_url+"\n")
import re
from urllib.parse import urlencode
from urllib.request import urlopen

import requests
from bs4 import BeautifulSoup
from scrapy.http import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import html
import unidecode
import sys
import json



class NewsSpider(CrawlSpider):
    '''
    This class is responsible for crawling globe and mail articles and their comments
    '''
    name = 'ScrapeNews'
    allowed_domains = ["theglobeandmail.com"]

    # base urls
    url_path = "../../Sample_Resources/Online_Resources/sample_base_urls.txt"
    start_urls = [line.strip() for line in open(url_path).readlines()]

    # Rules for including and excluding urls
    rules = (
        Rule(LinkExtractor(allow=r'\/.*\/article\d+\/$'), callback="parse_articles"),
    )

    def __init__(self, **kwargs):
        '''
        :param kwargs:
         Read user arguments and initialize variables
        '''
        CrawlSpider.__init__(self)
        self.startDate = kwargs['startDate']
        self.endDate = kwargs['endDate']
        print('startDate: ', self.startDate)
        print('self.endDate: ', self.endDate)

        self.article_folder = "../../Sample_Resources/Online_Resources/ArticleRawData/"
        self.comments_folder = "../../Sample_Resources/Online_Resources/CommentsRawData/"
        self.error_articles_file = "../../Sample_Resources/Online_Resources/error_article_ids.txt"
        self.error_comments_file = "../../Sample_Resources/Online_Resources/error_comments_article_ids.txt"
        self.empty_comments_file = "../../Sample_Resources/Online_Resources/empty_comment_article_ids.txt"

        self.headers = ({'User-Agent': 'Mozilla/5.0',
                         'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                         'X-Requested-With': 'XMLHttpRequest'})
        self.payload = {'username': 'mtaboada@sfu.ca', 'password': 'Negativity5'}
        self.apikey = '2_oNjjtSC8Qc250slf83cZSd4sbCzOF4cCiqGIBF8__5dWzOJY_MLAoZvds76cHeQD'
        self.categoryID = 'Production'
        self.ids_seen = set()


    def parse_articles(self, response):
        resp_url = response.url.strip()
        if resp_url in self.start_urls:
            article_ptn = "http://www.theglobeandmail.com/opinion/(.*?)/article(\d+)/"
            article_m = re.match(article_ptn, resp_url)
            article_id = ''
            if article_m != None:
                article_id = article_m.group(2)
                if article_id not in self.ids_seen:
                    self.ids_seen.add(article_id)

                    soup = BeautifulSoup(response.text, 'html.parser')
                    content_lst = soup.findAll('div', {"class":"column-2 gridcol"})
                    text = []
                    for content in content_lst:
                        if content != None and '<p>' in str(content):
                            text = ["<p>"+str(unidecode.unidecode(t.text))
                                                       .replace('\n', '').replace('\r', '').replace('\"', "'")+"</p>"
                                       for t in content.findAll('p', {"class":''})]
                            break

                    if len(text) > 0:
                        try:
                            published_date_str = str(soup.find("time", {"itemprop" : "datePublished"}))
                            pd_ptn = "datetime=\"(\d{4}-\d\d-\d\d)T\d\d:\d\d:\d\d(\w+)\""
                            m = re.search(pd_ptn, published_date_str)
                            published_date = ""
                            if m != None:
                                published_date = " ".join([m.group(1), m.group(2)])
                            else:
                                published_date_str = str(soup.find("meta", {"name" : "last-modified"}))
                                pd_ptn = "(\d{4}-\d\d-\d\d) \d\d:\d\d:\d\d (\w+)"
                                m = re.search(pd_ptn, published_date_str)
                                if m != None:
                                    published_date = " ".join([m.group(1), m.group(2)])
                                else:
                                    error_article = {article_id:{"data_type":"article", "article_url": resp_url,
                                                       "exception": "no published date"}}
                                    with open(self.error_articles_file, 'a') as error_articles:
                                        json.dump(error_article, error_articles)
                                        error_articles.write("\n")

                            if published_date >= self.startDate and published_date <= self.endDate:
                                article_author = soup.find("p", { "class" : "byline author vcard" })
                                if article_author != None:
                                    article_author = article_author.get_text().strip('\n')
                                else:
                                    article_author = "GLOBE EDITORIAL"
                                print('*****Article ID*****', article_id)
                                print('***Article URL***', resp_url)
                                print("*****Article *****", soup.title.string, article_author, published_date)

                                comments_url = resp_url + 'comments/'
                                article_data = {article_id: {"data_type":"article",
                                                    "title": unidecode.unidecode(soup.title.string),
                                                    "article_url": resp_url, "author":article_author,
                                                    "published_date":published_date, "article_text": text}}
                                article_file = self.article_folder + 'article_' + article_id + '.json'
                                with open(article_file, 'w') as article_out:
                                    json.dump(article_data, article_out)
                                yield Request(comments_url, callback=self.parse_comments)
                        except:
                            error_article = {article_id:{"data_type":"article", "article_url": resp_url,
                                                         "exception": str(sys.exc_info())}}
                            with open(self.error_articles_file, 'a') as error_articles:
                                        json.dump(error_article, error_articles)
                                        error_articles.write("\n")
                    else:
                        error_article = {article_id:{"data_type":"article", "article_url": resp_url,
                                                     "exception": "empty text"}}
                        with open(self.error_articles_file, 'a') as error_articles:
                                        json.dump(error_article, error_articles)
                                        error_articles.write("\n")
                        comments_url = resp_url + 'comments/'
                        yield Request(comments_url, callback=self.parse_comments)


    def parse_comments(self, response):

        print('****In Spider, Comment URL:**** ', response.url)
        comment_ptn = "http://www.theglobeandmail.com/(.*?)/article(\d+)/comments/"
        comment_m = re.match(comment_ptn, response.url)
        if comment_m != None:
            streamId = comment_m.group(2)
            session = requests.Session()
            resp = session.get(response.url, headers=self.headers)
            cookies = requests.utils.cookiejar_from_dict(requests.utils.dict_from_cookiejar(session.cookies))
            resp = session.post(response.url, headers=self.headers, data=self.payload, cookies=cookies)

            data = {"categoryID": self.categoryID,
                    "streamID": streamId,
                    "APIKey": self.apikey,
                    "callback": "foo",
                    "threadLimit": 1000   # assume all the articles have no more then 1000 comments
                    }
            r = urlopen("http://comments.us1.gigya.com/comments.getComments", data=urlencode(data).encode("utf-8"))

            comments_lst = json.loads(r.read().decode("utf-8"))["comments"]
            cleaned_comments = comments_lst
            if len(cleaned_comments) > 0:
                for i in range(len(cleaned_comments)):
                    cleaned_comments[i]['commentText'] = html.unescape(cleaned_comments[i]['commentText'])\
                        .replace('\n', '').replace('\r', '').replace('\"', "'")
                    if 'replies' in cleaned_comments[i].keys():
                        for j in range(len(cleaned_comments[i]['replies'])):
                            cleaned_comments[i]['replies'][j]['commentText'] = \
                                html.unescape(cleaned_comments[i]['replies'][j]['commentText'])\
                                    .replace('\n', '').replace('\r', '').replace('\"', "'")

            try:
                if len(cleaned_comments) > 0:
                    comments_data = {streamId: {"data_type": "comment", "comments": cleaned_comments}}
                    comments_file = self.comments_folder + 'article_' + streamId + '_comments.json'
                    with open(comments_file, 'w') as comments_out:
                        json.dump(comments_data, comments_out)
                else:
                    with open (self.empty_comments_file, 'a') as empty_comment_out:
                        empty_comment_out.write(streamId+"\n")
            except:
                with open(self.error_comments_file, 'a') as error_comment_out:
                    json.dump({streamId:{"exception": str(sys.exc_info())}}, error_comment_out)
                    error_comment_out.write("\n")
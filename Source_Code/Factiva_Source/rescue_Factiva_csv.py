# Check Factiva_uncaptured.csv to find articles can generate urls through Google CSE
# Update article data with captured url in Factiva_csv.csv, uncaptured still put in Factiva_uncaptured.csv
# The 2 types of search query used here are the same as generate_Factiva_csv.py
import re
import csv
from json import loads
from urllib.parse import urlencode
from urllib.request import urlopen
import time
import sys
from html.parser import HTMLParser


all_index = ['NS', 'IPD', 'LP', 'AN', 'CO', 'PG', 'WC', 'CX', 'TD', 'CLM', 'CR', 'PD', 'SE', 'HD', 'IN', 'BY', 'CY', 'LA', 'ED', 'RE', 'PUB', 'SC', 'SN']
custom_cols = ['Search_Query_1', 'Search_Query_2', 'URL', 'Article_ID']
result_dct = {}
uncaptured_dct = {}


# This class is used to clean HTML tags in text
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    '''
    Clean HTML tags in the text.
    :param html: text with HTML tags
    :return: cleaned text without HTML tag
    '''
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def get_article_id(article_url):
    '''
    Get article id from the url.
    :param article_url: an article url as the input
    :return: article id or empty
    '''
    ptn = "http://www.theglobeandmail.com/(.*?)/article(\d+)/"
    m = re.match(ptn, article_url)
    if m != None:
      return(m.group(2))
    return ''


def process_url(search_query):
    '''
    Get article url from Google CSE.
    :param search_query: a search query
    :return: article url and article id; or empty; or exception
    '''
    time.sleep(2)
    try:
        base_url = 'https://www.googleapis.com/customsearch/v1?'
        query = {
            'q': search_query,
            'format': 'json',
            'exactTerms': search_query,
            'cx': '[YOUR GOOGLE CSE ID]',      # YOU NEED TO SET CSE ID HERE
            'key': '[YOUR GOOGLE CSE KEY]',    # YOU NEED TO SET CSE KEY HERE
            'siteSearch': 'http://www.theglobeandmail.com/*'
        }

        url = base_url + urlencode(query)
        response = urlopen(url)
        quote = loads(response.read().decode("utf-8"))
        if 'items' in quote.keys():
            for elem in quote['items']:
                if 'pagemap' in elem.keys():
                    if 'metatags' in elem['pagemap'].keys():
                        if len(elem['pagemap']['metatags']) > 0:
                            if 'og:url' in elem['pagemap']['metatags'][0].keys():
                                article_url = (elem['pagemap']['metatags'][0]['og:url'])
                                article_id = get_article_id(article_url)
                                return(article_url, article_id)
        return('', '')
    except:
        print('exception', sys.exc_info())
        print(search_query)
        return('exception', 'exception')



def main():
    captured_file = "../../Sample_Resources/Factiva_CSV/Factiva_csv.csv"     # YOU MAY NEED TO CHANGE THE PATH HERE
    uncaptured_file = "../../Sample_Resources/Factiva_CSV/Factiva_uncaptured.csv"  # YOU MAY NEED TO CHANGE THE PATH HERE

    exception_count = 0
    exception_limit = 10     # YOU MAY WANT TO SET THE EXCEPTION THRESHOLD HERE

    with open(uncaptured_file) as csvfile:
        f = csv.DictReader(csvfile)
        for r in f:
            file_idx = r['Page-Article']
            print(file_idx)

            if exception_count > exception_limit:    # this happened when you used all Google CSE daily limit
                uncaptured_dct[file_idx] = r
                continue

            if r['Search_Query_1'] == '' and r['Search_Query_2'] == '' and r['LP'] != '':
                lp_data = strip_tags(r['LP'])
                rescue_url, rescure_article_id = process_url(lp_data)
                r['URL'] = rescue_url
                r['Article_ID'] = rescure_article_id
                if 'article' not in rescue_url:
                    if rescure_article_id == 'exception':
                        exception_count += 1
                    uncaptured_dct[file_idx] = r
                else: result_dct[file_idx] = r
            elif r['URL'] == 'exception':
                rescue_url, rescure_article_id = process_url(r['Search_Query_1'])
                if 'article' not in rescue_url:
                    rescue_url, rescure_article_id = process_url(r['Search_Query_2'])
                r['URL'] = rescue_url
                r['Article_ID'] = rescure_article_id
                if 'article' not in rescue_url:
                    if rescure_article_id == 'exception':
                        exception_count += 1
                    uncaptured_dct[file_idx] = r
                else: result_dct[file_idx] = r
            else:
                uncaptured_dct[file_idx] = r

    # data with captured url will be appended into captured csv file
    with open(captured_file, 'a') as csv_output:
        fieldnames = ['Page-Article']
        fieldnames.extend(all_index)
        fieldnames.extend(custom_cols)
        writer = csv.DictWriter(csv_output, fieldnames=fieldnames)

        for page_article, page_dct in result_dct.items():
            writer.writerow({'Page-Article':page_article, 'NS':page_dct['NS'], 'IPD':page_dct['IPD'],
                             'LP':page_dct['LP'], 'AN':page_dct['AN'], 'CO':page_dct['CO'], 'PG':page_dct['PG'],
                             'WC':page_dct['WC'], 'CX':page_dct['CX'], 'TD':page_dct['TD'], 'CLM':page_dct['CLM'],
                             'CR':page_dct['CR'], 'PD':page_dct['PD'], 'SE':page_dct['SE'], 'HD':page_dct['HD'],
                             'IN':page_dct['IN'], 'BY':page_dct['BY'], 'CY':page_dct['CY'], 'LA':page_dct['LA'],
                             'ED':page_dct['ED'], 'RE':page_dct['RE'], 'PUB':page_dct['PUB'], 'SC':page_dct['SC'],
                             'SN':page_dct['SN'], 'Search_Query_1':page_dct['Search_Query_1'], 'Search_Query_2':page_dct['Search_Query_2']
                             ,'URL':page_dct['URL'], 'Article_ID':page_dct['Article_ID']
                             })

    # data without captured url will be appended into uncaptured csv file
    with open(uncaptured_file, 'wt') as csv_output:
        fieldnames = ['Page-Article']
        fieldnames.extend(all_index)
        fieldnames.extend(custom_cols)
        writer = csv.DictWriter(csv_output, fieldnames=fieldnames)
        writer.writeheader()

        for page_article, page_dct in uncaptured_dct.items():
            writer.writerow({'Page-Article':page_article, 'NS':page_dct['NS'], 'IPD':page_dct['IPD'],
                             'LP':page_dct['LP'], 'AN':page_dct['AN'], 'CO':page_dct['CO'], 'PG':page_dct['PG'],
                             'WC':page_dct['WC'], 'CX':page_dct['CX'], 'TD':page_dct['TD'], 'CLM':page_dct['CLM'],
                             'CR':page_dct['CR'], 'PD':page_dct['PD'], 'SE':page_dct['SE'], 'HD':page_dct['HD'],
                             'IN':page_dct['IN'], 'BY':page_dct['BY'], 'CY':page_dct['CY'], 'LA':page_dct['LA'],
                             'ED':page_dct['ED'], 'RE':page_dct['RE'], 'PUB':page_dct['PUB'], 'SC':page_dct['SC'],
                             'SN':page_dct['SN'], 'Search_Query_1':page_dct['Search_Query_1'], 'Search_Query_2':page_dct['Search_Query_2']
                             ,'URL':page_dct['URL'], 'Article_ID':page_dct['Article_ID']
                             })

if __name__ == "__main__":
    main()
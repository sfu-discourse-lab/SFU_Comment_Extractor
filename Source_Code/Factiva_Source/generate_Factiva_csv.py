# Collect Factiva data into .csv based on its index
# Generate search query based on each article text
# Use Google Custom Search Engine (CSE) to get urls
# Articles with captured URL and Article_ID will all be append in 1 file, uncaptured will be append in the other file
from bs4 import BeautifulSoup
import re
import csv
from json import loads
from urllib.parse import urlencode
from urllib.request import urlopen
import time
import os
import sys


all_index = ['NS', 'IPD', 'LP', 'AN', 'CO', 'PG', 'WC', 'CX', 'TD', 'CLM', 'CR', 'PD', 'SE', 'HD', 'IN', 'BY', 'CY', 'LA', 'ED', 'RE', 'PUB', 'SC', 'SN']
custom_cols = ['Search_Query_1', 'Search_Query_2', 'URL', 'Article_ID']
exclude_SE = ['Globe Life Column', 'Report on Business', 'Sports Column', 'The Globe Review Column', 'Travel Column', 'Weekend Review Column']
result_dct = {}
uncaptured_dct = {}


def in_exclude_list(itm, exclude_lst):
    '''
    Since articles with a specific SE value are not news, they should be excluded.
    :param itm: a Factiva article data
    :param exclude_lst: SE values that should be excluded
    :return: True or False
    '''
    for e in exclude_lst:
        if e in itm: return True
    return False


def create_tmp_dct():
    '''
    Create an empty dictionary for an article,
    the dictionary keys are the .csv columns.
    :return: an empty dictionary with all .csv columns
    '''
    tmp_dct = {}
    for elem in all_index:
        tmp_dct[elem] = ''
    return tmp_dct


def get_search_query_1(td_text, n):
    '''
    Generate Type 1 search query, it is using the first n words from Factiva index TD.
    :param td_text: Factiva index TD text of an article
    :param n: set n
    :return: first n words from TD text
    '''
    soup = BeautifulSoup(td_text, "lxml")
    all_tags = soup.find_all('p')
    ptn = '<p class=\"articleParagraph enarticleParagraph\">\n*(.*?)\n*</p>'
    for tg in all_tags:
        if 'articleParagraph enarticleParagraph' in str(tg):
            m = re.match(ptn, str(tg))
            if m != None:
                mt = m.group(1)
                s = BeautifulSoup(mt,  "lxml").get_text().split()
                if len(s) >= n:
                    lst = []
                    for i in range(n):
                        lst.append(s[i])
                    return(' '.join(lst))


def get_search_query_2(td_text):
    '''
    Generate Type 2 search query, it is using the second paragraph first 300 characteristics from Factiva index TD.
    :param td_text: Factiva index TD text of an article
    :return: first 300 characteristics of TD second paragraph
    '''
    soup = BeautifulSoup(td_text, "lxml")
    all_tags = soup.find_all('p')
    ptn = '<p class=\"articleParagraph enarticleParagraph\">\n*(.*?)\n*</p>'
    is_first = 0
    min_len = 10
    pback_up = ""

    for tg in all_tags:
        if 'articleParagraph enarticleParagraph' in str(tg) and is_first == 0:
            is_first = 1
            continue
        elif 'articleParagraph enarticleParagraph' in str(tg) and is_first == 1:
            m = re.match(ptn, str(tg))
            if m != None:
                mt = m.group(1)
                s = BeautifulSoup(mt,  "lxml").get_text()
                if len(s.split()) < min_len:
                    pback_up = s
                    continue
                if len(s) > 300: return s[0:300]
                else: return s
    return pback_up


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
            'siteSearch': 'http://www.theglobeandmail.com/*'     # THE SEARCH SITE IS GLOBE AND MAIL
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
        return('exception', 'exception')


def get_all_content(soup, page_num, yr):
    '''
    Get all the columns value for each article,
    the columns include those in all_index, search query Type 1, Type 2, generated url and article id.
    :param soup: Python BeautifulSoup parsed data from each downloaded .htm file
    :param page_num: Factiva page number of the article, each page normally contains 100 articles or less
    :param yr: the year of the article
    :return: number of exceptions
     meanwhile it adds captured content into result_dct; adds uncaptured content into uncaptured_dct
    '''
    top_tag = ['b', 'td']

    idx_ptn = "<b>(\w\w\w*)</b>"
    value_ptn = "<td>\n*(.*?)\n*</td>"

    all_tags = soup.find_all(top_tag)
    is_idx = 0
    article_count = 0
    idx = ''
    is_article_start = 1
    has_exception = 0

    tmp_dct = {}

    for tg in all_tags:
        m1 = re.match(idx_ptn, str(tg))
        m2 = re.match(value_ptn, str(tg))
        m3 = re.match(value_ptn, str(tg).replace('\n', ''))
        if m1 != None:
            idx = m1.group(1)
            if idx in all_index:
                is_idx = 1
                if is_article_start == 1:
                    is_article_start = 0
                    tmp_dct = create_tmp_dct()
        elif m2 != None and is_idx == 1:
            is_idx = 0
            idx_value = BeautifulSoup(m2.group(1),  "lxml").get_text()
            tmp_dct[idx] = idx_value
            if idx == 'AN':
                is_article_start = 1
                article_count += 1
                k = str(yr) + '-Page' + str(page_num) + '-' + str(article_count)
                print(k)
                if in_exclude_list(tmp_dct['SE'], exclude_SE) == False:
                    tmp_dct['Search_Query_1'] = get_search_query_1(tmp_dct['TD'], 10)
                    tmp_dct['Search_Query_2'] = get_search_query_2(tmp_dct['TD'])
                    article_url, article_id = process_url(tmp_dct['Search_Query_1'])
                    if article_url == '':
                        article_url, article_id = process_url(tmp_dct['Search_Query_2'])
                    tmp_dct['URL'] = article_url
                    tmp_dct['Article_ID'] = article_id
                    if article_id == '' or article_id == 'exception':
                        uncaptured_dct[k] = tmp_dct
                        if article_id == 'exception':
                            has_exception += 1
                    else: result_dct[k] = tmp_dct
        elif m3 != None and is_idx == 1:
            is_idx = 0
            idx_value = m3.group(1)
            tmp_dct[idx] = idx_value
            if idx == 'AN':
                is_article_start = 1
                article_count += 1
                k = str(yr) + '-Page' + str(page_num) + '-' + str(article_count)
                print(k)
                if in_exclude_list(tmp_dct['SE'], exclude_SE) == False:
                    tmp_dct['Search_Query_1'] = get_search_query_1(tmp_dct['TD'], 10)
                    tmp_dct['Search_Query_2'] = get_search_query_2(tmp_dct['TD'])
                    article_url, article_id = process_url(tmp_dct['Search_Query_1'])
                    if article_url == '':
                        article_url, article_id = process_url(tmp_dct['Search_Query_2'])
                    tmp_dct['URL'] = article_url
                    tmp_dct['Article_ID'] = article_id
                    if article_id == '' or article_id == 'exception':
                        uncaptured_dct[k] = tmp_dct
                        if article_id == 'exception':
                            has_exception += 1
                    else: result_dct[k] = tmp_dct
    return has_exception


def get_uncaptured_content(soup, page_num, yr):
    '''
    This function is used when daily Google CSE limit has been used,
    and therefore the rest articles will only get exception.
    In order to save time, this function will directly add the rest unchecked articles' data into uncaptured_dct.
    :param soup: Python BeautifulSoup parsed data from each downloaded .htm file
    :param page_num: Factiva page number of the article, each page normally contains 100 articles or less
    :param yr: the year of the article
    :return: None
    '''
    top_tag = ['b', 'td']

    idx_ptn = "<b>(\w\w\w*)</b>"
    value_ptn = "<td>\n*(.*?)\n*</td>"

    all_tags = soup.find_all(top_tag)
    is_idx = 0
    article_count = 0
    idx = ''
    is_article_start = 1

    tmp_dct = {}

    for tg in all_tags:
        m1 = re.match(idx_ptn, str(tg))
        m2 = re.match(value_ptn, str(tg))
        m3 = re.match(value_ptn, str(tg).replace('\n', ''))
        if m1 != None:
            idx = m1.group(1)
            if idx in all_index:
                is_idx = 1
                if is_article_start == 1:
                    is_article_start = 0
                    tmp_dct = create_tmp_dct()
        elif m2 != None and is_idx == 1:
            is_idx = 0
            idx_value = BeautifulSoup(m2.group(1),  "lxml").get_text()
            tmp_dct[idx] = idx_value
            if idx == 'AN':
                is_article_start = 1
                article_count += 1
                k = str(yr) + '-Page' + str(page_num) + '-' + str(article_count)
                print(k)
                if in_exclude_list(tmp_dct['SE'], exclude_SE) == False:
                    tmp_dct['Search_Query_1'] = get_search_query_1(tmp_dct['TD'], 10)
                    tmp_dct['Search_Query_2'] = get_search_query_2(tmp_dct['TD'])
                    tmp_dct['URL'] = 'exception'
                    tmp_dct['Article_ID'] = 'exception'
                    uncaptured_dct[k] = tmp_dct
        elif m3 != None and is_idx == 1:
            is_idx = 0
            idx_value = m3.group(1)
            tmp_dct[idx] = idx_value
            if idx == 'AN':
                is_article_start = 1
                article_count += 1
                k = str(yr) + '-Page' + str(page_num) + '-' + str(article_count)
                print(k)
                if in_exclude_list(tmp_dct['SE'], exclude_SE) == False:
                    tmp_dct['Search_Query_1'] = get_search_query_1(tmp_dct['TD'], 10)
                    tmp_dct['Search_Query_2'] = get_search_query_2(tmp_dct['TD'])
                    tmp_dct['URL'] = 'exception'
                    tmp_dct['Article_ID'] = 'exception'
                    uncaptured_dct[k] = tmp_dct


def main():
    factiva_downloads = "../../Sample_Resources/Factiva_Downloads/"     # YOU MAY NEED TO CHANGE THE PATH HERE
    factiva_csv_folder = "../../Sample_Resources/Factiva_CSV/"
    start_year = 2012      # YOU MAY NEED TO CHANGE THE START YEAR HERE
    end_year = 2013        # YOU MAY NEED TO CHANGE THE END YEAR HERE

    for yr in range(start_year, end_year+1):
        factiva_data_folder = factiva_downloads + str(yr) + "/"
        page_num = len([f for f in os.listdir(factiva_data_folder)
                    if os.path.isfile(factiva_data_folder+"/"+f) and '.htm' in f])
        file_path_pre = factiva_data_folder+"Factiva_"+str(yr)+"_"
        captured_output_path = factiva_csv_folder + "Factiva_csv.csv"
        uncaptured_output_path =  factiva_csv_folder + "Factiva_uncaptured.csv"
        exception_count = 0
        exception_limit = 10     # YOU MAY WANT TO SET THE EXCEPTION THRESHOLD HERE

        for i in range(page_num):
            file_path = file_path_pre + str(1+i) + ".htm"
            ecj_data = open(file_path,'r').read()
            soup = BeautifulSoup(ecj_data, "lxml")
            if exception_count >= exception_limit:    # this happened when you used all Google CSE daily limit
                get_uncaptured_content(soup, i+1, yr)
                continue
            exception_count += get_all_content(soup, i+1, yr)

        # data with captured url will be appended into captured csv file
        with open(captured_output_path, 'a') as csv_output:
            fieldnames = ['Page-Article']
            fieldnames.extend(all_index)
            fieldnames.extend(custom_cols)
            writer = csv.DictWriter(csv_output, fieldnames=fieldnames)
            if os.path.isfile(captured_output_path) and os.stat(captured_output_path).st_size == 0:
                writer.writeheader()

            for page_article, page_dct in result_dct.items():
                writer.writerow({'Page-Article':page_article, 'NS':page_dct['NS'], 'IPD':page_dct['IPD'],
                                 'LP':page_dct['LP'], 'AN':page_dct['AN'], 'CO':page_dct['CO'], 'PG':page_dct['PG'],
                                 'WC':page_dct['WC'], 'CX':page_dct['CX'], 'TD':page_dct['TD'], 'CLM':page_dct['CLM'],
                                 'CR':page_dct['CR'], 'PD':page_dct['PD'], 'SE':page_dct['SE'], 'HD':page_dct['HD'],
                                 'IN':page_dct['IN'], 'BY':page_dct['BY'], 'CY':page_dct['CY'], 'LA':page_dct['LA'],
                                 'ED':page_dct['ED'], 'RE':page_dct['RE'], 'PUB':page_dct['PUB'], 'SC':page_dct['SC'],
                                 'SN':page_dct['SN'], 'Search_Query_1':page_dct['Search_Query_1'],
                                 'Search_Query_2':page_dct['Search_Query_2']
                                 ,'URL':page_dct['URL'], 'Article_ID':page_dct['Article_ID']
                                 })

        # data without captured url will be appended into uncaptured csv file
        with open(uncaptured_output_path, 'a') as csv_output:
            fieldnames = ['Page-Article']
            fieldnames.extend(all_index)
            fieldnames.extend(custom_cols)
            writer = csv.DictWriter(csv_output, fieldnames=fieldnames)
            if os.path.isfile(uncaptured_output_path) and os.stat(uncaptured_output_path).st_size == 0:
                writer.writeheader()

            for page_article, page_dct in uncaptured_dct.items():
                writer.writerow({'Page-Article':page_article, 'NS':page_dct['NS'], 'IPD':page_dct['IPD'],
                                 'LP':page_dct['LP'], 'AN':page_dct['AN'], 'CO':page_dct['CO'], 'PG':page_dct['PG'],
                                 'WC':page_dct['WC'], 'CX':page_dct['CX'], 'TD':page_dct['TD'], 'CLM':page_dct['CLM'],
                                 'CR':page_dct['CR'], 'PD':page_dct['PD'], 'SE':page_dct['SE'], 'HD':page_dct['HD'],
                                 'IN':page_dct['IN'], 'BY':page_dct['BY'], 'CY':page_dct['CY'], 'LA':page_dct['LA'],
                                 'ED':page_dct['ED'], 'RE':page_dct['RE'], 'PUB':page_dct['PUB'], 'SC':page_dct['SC'],
                                 'SN':page_dct['SN'], 'Search_Query_1':page_dct['Search_Query_1'],
                                 'Search_Query_2':page_dct['Search_Query_2']
                                 ,'URL':page_dct['URL'], 'Article_ID':page_dct['Article_ID']
                                 })

if __name__ == "__main__":
    main()
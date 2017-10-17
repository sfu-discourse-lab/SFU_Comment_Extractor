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
import argparse
import pandas as pd
from html.parser import HTMLParser


all_index = ['NS', 'IPD', 'LP', 'AN', 'CO', 'PG', 'WC', 'CX', 'TD', 'CLM', 'CR', 'PD', 'SE', 'HD', 'IN', 'BY', 'CY', 'LA', 'ED', 'RE', 'PUB', 'SC', 'SN']
#custom_cols = ['Search_Query_1', 'Search_Query_2', 'URL', 'Article_ID']
counter_dct = {}
result_dct = {}
uncaptured_dct = {}
exclude_SE = ['Globe Life Column', 'Report on Business', 'Sports Column', 'The Globe Review Column', 'Travel Column', 'Weekend Review Column']


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
    html = str(html)
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def clean_csv(input_csv, output_csv):
    #df = pd.read_csv('/Users/vkolhatk/for_katharina/factiva_csv/Factiva_uncaptured.csv')
    df = pd.read_csv(input_csv)
    df['clean_LP'] = df.LP.apply(strip_tags)
    df['clean_TD'] = df.TD.apply(strip_tags)
    df['article_text'] = df[['clean_LP', 'clean_TD']].apply(lambda x: ' '.join(x), axis=1)
    df.to_csv(output_csv)
    print('Output written: ', output_csv)

for elem in all_index:
    counter_dct[elem] = {'idx_count':0, 'value_count':0}

def in_exclude_list(itm, exclude_lst):
    for e in exclude_lst:
        if e in itm: return True
    return False

def create_tmp_dct():
    tmp_dct = {}
    for elem in all_index:
        tmp_dct[elem] = ''
    return tmp_dct

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
                result_dct[k] = tmp_dct
        elif m3 != None and is_idx == 1:
            is_idx = 0
            idx_value = m3.group(1)
            tmp_dct[idx] = idx_value
            if idx == 'AN':
                is_article_start = 1
                article_count += 1
                k = str(yr) + '-Page' + str(page_num) + '-' + str(article_count)
                print(k)
                result_dct[k] = tmp_dct

def factiva_html_to_csv(factiva_downloads, factiva_csv_folder,
                        start_year, end_year, output_csv_file):
    '''
    :param factiva_downloads:
    :param factiva_csv_folder:
    :param start_year:
    :param end_year:
    :param output_csv_file:
    :return:
    '''

    for yr in range(start_year, end_year+1):
        factiva_data_folder = factiva_downloads + str(yr) + "/"
        page_num = len([f for f in os.listdir(factiva_data_folder)
                    if os.path.isfile(factiva_data_folder+"/"+f) and '.html' in f])
        file_path_pre = factiva_data_folder+"Factiva_"+str(yr)+"_"
        captured_output_path = factiva_csv_folder + "Factiva_csv.csv"            # YOU MAY NEED TO CHANGE THE PATH HERE

        for i in range(page_num):
            file_path = file_path_pre + str(1+i) + ".html"
            print('file path: ', file_path)
            ecj_data = open(file_path,'r').read()
            #print('ecj_data: ', ecj_data)
            soup = BeautifulSoup(ecj_data, "lxml")
            #print(soup)
            #sys.exit(0)
            get_all_content(soup, i+1, yr)
        # data with captured url will be appended into captured csv file
        with open(captured_output_path, 'w') as csv_output:
            fieldnames = ['Page-Article']
            fieldnames.extend(all_index)
            #fieldnames.extend(custom_cols)
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
                                 'SN':page_dct['SN']
                                 })
        print('CSV written: ', captured_output_path)
        print('Cleaning the CSV: ')
        clean_csv(captured_output_path, factiva_csv_folder + output_csv_file)

def get_arguments():
    parser = argparse.ArgumentParser(description='Create a subset CSV of the given CSV')

    parser.add_argument('--input_dir', '-i', type=str, dest='factiva_input_dir', action='store',
                        default = './factiva/',
                        help="Input directory containing factiva data")

    parser.add_argument('--output_dir', '-o', type=str, dest='factiva_output_dir', action='store',
                        default = './factiva_csv/',
                        help="Input directory containing factiva data")

    parser.add_argument('--start_year', '-s', type=int, dest='start', action='store',
                        default = 2013,
                        help="Start year")

    parser.add_argument('--end_year', '-e', type=int, dest='end', action='store',
                        default = 2013,
                        help="End year")

    parser.add_argument('--output_csv', '-oc', type=str, dest='output_csv_file', action='store',
                        default = 'news_data.csv',
                        help="output csv")

    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = get_arguments()
    print(args)
    factiva_csv_file = factiva_html_to_csv(args.factiva_input_dir, args.factiva_output_dir,
                                   args.start, args.end, args.output_csv_file)




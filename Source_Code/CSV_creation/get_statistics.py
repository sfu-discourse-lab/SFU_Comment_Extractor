__author__ = 'Varada Kolhatkar'
import argparse, sys, os, glob
import pandas as pd
import re
from timeit import default_timer as timer
import string
import numpy as np

def get_arguments():
    parser = argparse.ArgumentParser(description='Write csv files for crowd annotation')

    parser.add_argument('--comments_csv', '-c', type=str, dest='comments_csv', action='store',
                        default=r'/Users/vkolhatk/Data/GnM_CSVs/Final_csvs/gnm_comments.csv',
                        help="the comments csv file")

    parser.add_argument('--articles_csv', '-a', type=str, dest='articles_csv', action='store',
                        default=r'/Users/vkolhatk/Data/GnM_CSVs/Final_csvs/gnm_articles.csv',
                        help="the articles csv file")

    parser.add_argument('--output', '-o', type=str, dest='output', action='store',
                        default='/Users/vkolhatk/Data/GnM_CSVs/intermediate_csvs/stats.csv',
                        help="the output csv file")

    args = parser.parse_args()
    return args

def get_article_stats(adf):
    '''
    :param adf: (pandas.DataFrame)
    :return: (dict)
    Description: Given an article datafrane adf, this function returns a dictionary containing article stats.
    '''
    article_stats_dict = {}

    # Get Number of articles
    article_stats_dict['narticles'] = adf.shape[0]

    # Number of authors
    s = adf.groupby('author')['article_id'].nunique()
    article_stats_dict['nauthors'] = len(s)

    return article_stats_dict

def get_comments_stats(adf, cdf):
    '''
    :param adf: (pandas.DataFrame)
    :return: (dict)
    Description: Given an article datafrane adf, this function returns a dictionary containing comments stats.
    '''
    comment_stats_dict = {}
    return comment_stats_dict

def get_stats(articles_csv, comments_csv, output_csv):
    '''
    :param articles_csv: (str)
    :param comments_csv: (str)
    :param output_csv: (str)
    :return: None
    Description Get article and comment stats and write a CSV output_csv containing the stats
    '''
    # Get article stats
    adf = pd.read_csv(articles_csv)
    cdf = pd.read_csv(comments_csv)
    article_stats = get_article_stats(adf)

    # Get comment stats
    comments_stats = get_comments_stats(adf, cdf)

    # Combine article and comment stats
    stats_dict = {**article_stats, **comments_stats}

    # Write the stats dict as a CSV with key and values as columns
    df = pd.DataFrame.from_dict(stats_dict, orient='index')
    df.index.name = 'variable'
    df.columns = ['stats']
    df.to_csv(output_csv)
    print('Data stats written in file: ', output_csv)

if __name__ == "__main__":
    args = get_arguments()
    print(args)
    start = timer()
    print('Start time: ', start)
    get_stats(args.articles_csv, args.comments_csv, args.output)
    end = timer()
    print('Total time taken: ', end-start)

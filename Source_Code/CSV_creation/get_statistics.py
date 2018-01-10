__author__ = 'Varada Kolhatkar'
import argparse
import pandas as pd
from timeit import default_timer as timer
import re


def get_arguments():
    parser = argparse.ArgumentParser(description='Write csv files for crowd annotation')

    parser.add_argument('--comments_csv', '-c', type=str, dest='comments_csv', action='store',
                        default=r'/Users/Mehvish/Documents/SFU/Semester2/linguistics/CSVs/gnm_comments.csv',
                        help="the comments csv file")

    parser.add_argument('--articles_csv', '-a', type=str, dest='articles_csv', action='store',
                        default=r'/Users/Mehvish/Documents/SFU/Semester2/linguistics/CSVs/gnm_articles.csv',
                        help="the articles csv file")

    parser.add_argument('--output', '-o', type=str, dest='output', action='store',
                        default='/Users/Mehvish/Documents/SFU/Semester2/linguistics/CSVs/stats.csv',
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

    # Number of words
    words = adf.apply(lambda row: len(re.sub('<p>|</p>', '', row['article_text']).split()), axis=1)
    article_stats_dict['nwords_articles'] = sum(words)

    return article_stats_dict


def get_comments_stats(adf, cdf):
    '''
    :param adf: (pandas.DataFrame)
    :return: (dict)
    Description: Given an article datafrane adf, this function returns a dictionary containing comments stats.
    '''
    comment_stats_dict = {}
    comment_per_author = {}

    # Number of words in comments
    words = cdf.apply(lambda row: len(row['comment_text'].split()), axis=1)
    comment_stats_dict['nwords_comments'] = sum(words)

    adf = adf[adf['ncomments'] != 0]

    # Average number of comments per article
    comment_stats_dict['avg_comments'] = round(sum(adf['ncomments']) / adf.shape[0])

    # Average number of top level comments per article
    comment_stats_dict['avg_top_level_comm'] = round(sum(adf['ntop_level_comments']) / adf.shape[0])

    # Number of unique commenters
    comment_stats_dict['ncommenters'] = cdf['author'].nunique()

    # Average number of comments per commenter
    comments = cdf.groupby(cdf['author'], as_index=False).count()
    comment_per_author['commenter'] = comments['author']
    comment_per_author['ncomments'] = comments['comment_text']

    comment_stats_dict['avg_comm_per_author'] = round(sum(comment_per_author['ncomments']) / comments.shape[0])

    return comment_stats_dict, comment_per_author


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
    comments_stats, comment_per_author = get_comments_stats(adf, cdf)

    # Combine article and comment stats
    stats_dict = {**article_stats, **comments_stats}

    # Write the stats dict as a CSV with key and values as columns
    df = pd.DataFrame.from_dict(stats_dict, orient='index')
    commenter_df = pd.DataFrame.from_dict(comment_per_author)

    df.index.name = 'variable'
    df.columns = ['stats']
    df.to_csv(output_csv)
    commenter_df.to_csv("commenter_output.csv", index=False)
    print('Data stats written in file: ', output_csv)


if __name__ == "__main__":
    args = get_arguments()
    print(args)
    start = timer()
    print('Start time: ', start)
    get_stats(args.articles_csv, args.comments_csv, args.output)
    end = timer()
    print('Total time taken: ', end-start)

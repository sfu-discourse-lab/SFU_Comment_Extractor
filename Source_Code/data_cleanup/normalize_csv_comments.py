__author__ = 'Varada Kolhatkar'
import argparse, sys, os, glob, ntpath, pprint, codecs, re, csv
import pandas as pd
import re, html.entities
from timeit import default_timer as timer
import string
import numpy as np
import multiprocessing as mp
from multiprocessing import cpu_count
import re


def word_segmentation(text):
    '''
    :param text: (str)
    :param dictionary: (list)
    :return: (str) word segmented text
     Given a text, this code converts into word-segmented text and returns it. It retains the case, punctuation while
     doing the word segmentation.
    '''
    #dictionary = read_dictionary()
    #translator = str.maketrans('', '', string.punctuation)
    word_segmented_text = ''
    missing_space_obj = re.compile(r'(?P<prev_word>(^|\s)\w{3,25}[.,?!;:]{1,3})(?P<next_word>(\w+))')

    def repl(m):
        return m.group('prev_word') + ' ' + m.group('next_word')

    # Separate words on punctuation. This will take care of following examples:
    # Rich,This => Rich, This
    #
    text = missing_space_obj.sub(repl, text)
    return text

def unescape(text):
    '''
    :param text:
    :return:
     Description
    ##
    # Removes HTML or XML character references and entities from a text string.
    #
    # @param text The HTML (or XML) source text.
    # @return The plain text, as a Unicode string, if necessary.
    # AUTHOR: Fredrik Lundh
    '''
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return chr(int(text[3:-1], 16))
                else:
                    return chr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = chr(html.entities.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

def clean_text(text):
    '''
    :param text:
    :return:
    '''
    text = text.strip()
    text = " ".join(text.split())
    text = text.replace(r"`",r"'")
    text = re.sub(r'\(In reply to:.*?--((\s\S+){1,10})?\)', '', text)
    return text

def normalize(text):
    '''
    :param input_csv:
    :param output_csv:
    :param column:
    :param dictionary:
    :return:
    '''
    try:
        cleaned = clean_text(text)
        text_ws = word_segmentation(cleaned)
        text_preprocessed = unescape(text_ws)
    except:
        print('------------')
        print('Problem text: ', text)
        print('------------')
        text_preprocessed = text
    return text_preprocessed

def run_normalize(df):
    '''
    :param df:
    :return:
    '''
    df['text_preprocessed'] = df['text'].apply(normalize)
    return df

def get_arguments():
    parser = argparse.ArgumentParser(description='Write csv files for crowd annotation')
    parser.add_argument('--input_csv', '-i', type=str, dest='input_csv', action='store',
                        #default='/Users/vkolhatk/Data/GnM_CSVs/intermediate_csvs/new_comments.csv',
                        #default='/Users/vkolhatk/Data/GnM_CSVs/intermediate_csvs/old_comments.csv',
                        default='../../Sample_Resources/Sample_Comments_CSVs/comments_csv_sample.csv',
                        help="the input csv file")

    parser.add_argument('--output_csv', '-o', type=str, dest='output_csv', action='store',
                        #default='/Users/vkolhatk/Data/GnM_CSVs/intermediate_csvs/new_comments_preprocessed.csv',
                        #default='/Users/vkolhatk/Data/GnM_CSVs/intermediate_csvs/old_comments_preprocessed.csv',
                        default='../../Sample_Resources/Sample_Comments_CSVs/comments_csv_sample_preprocessed.csv',
                        help="the output csv file")

    parser.add_argument('--columns_to_write', '-cw', type=list, dest='cols', action='store',
                        # For new comments
                        #default=['article_id','comment_counter','ID','text','text_preprocessed', 'timestamp', 'TotalVotes','negVotes','posVotes','author'],
                        # for old comments
                        default =['article_id','comment_counter','comment_id','text','text_preprocessed','reactions','post_time','replies','author'],
                        help="the output csv file")

    #parser.add_argument('--column_to_preprocess', '-c', type=str, dest='column_name', action='store',
    #                    default='text',
    #                    help="the column to preprocess")

    args = parser.parse_args()
    return args

def parallelize(data, func):
    data_split = np.array_split(data, partitions)
    pool = mp.Pool(cores)
    data = pd.concat(pool.map(func, data_split))
    pool.close()
    pool.join()
    return data

if __name__ == "__main__":
    args = get_arguments()
    print(args)

    #Read dictionary
    #dictionary = read_dictionary()
    start = timer()
    print('Start time: ', start)
    cores = cpu_count()
    partitions = cores
    df = pd.read_csv(args.input_csv)
    df_processed = parallelize(df, run_normalize)
    df_processed.to_csv(args.output_csv, columns=args.cols, index=False)
    print('Output csv written: ', args.output_csv)
    end = timer()

    print('Total time taken: ', end-start)

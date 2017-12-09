__author__ = 'Varada Kolhatkar'
import argparse, sys, os, glob, ntpath, pprint, codecs, re, csv
import pandas as pd
import wordsegment
from wordsegment import segment
from autocorrect import spell
from autocorrect import known
import re, html.entities
from timeit import default_timer as timer
import string
import numpy as np
import multiprocessing as mp
from multiprocessing import cpu_count
import re


def read_dictionary(dictionary_file=wordsegment.DATADIR + '/unigrams.txt'):
    '''
    :param path:
    :return:
    '''
    uni_dictionary = []
    missed_words = ['ipads']
    unigrams = wordsegment.parse_file(dictionary_file)
    for (word, count) in unigrams.items():
        uni_dictionary.append(word)
    for w in missed_words:
        uni_dictionary.append(w)
    print(len(uni_dictionary))
    return uni_dictionary

def retain_case(word, segments):
    '''
    :param word:
    :param segments:
    :return:
    '''
    counter = 0
    orig_case_segments = []
    for segment in segments:
        orig_case_segment = ''
        for ch in segment:
            if word[counter].lower() == ch:
                orig_case_segment += word[counter]
            counter += 1
        orig_case_segments.append(orig_case_segment)

    return orig_case_segments


def auto_correction(word, dictionary):
    '''
    :param word:
    :param dictionary:
    :return:
    '''

    #print('Word', word.lower(), ' is in the dictionary', word in dictionary)
    if len(word) > 4 and \
        not word.isupper() and\
        not word.lower() in dictionary:
        word = spell(word)
    return(word)


def word_segmentation(text):
    '''
    :param text: (str)
    :param dictionary: (list)
    :return: (str) word segmented text
     Given a text, this code converts into word-segmented text and returns it. It retains the case, punctuation while
     doing the word segmentation.
    '''
    #dictionary = read_dictionary()
    translator = str.maketrans('', '', string.punctuation)
    word_segmented_text = ''
    missing_space_obj = re.compile(r'(?P<prev_word>(^|\s)\w{3,25}[.,?!;:]{1,3})(?P<next_word>(\w+))')

    def repl(m):
        return m.group('prev_word') + ' ' + m.group('next_word')

    # Separate words on punctuation. This will take care of following examples:
    # Rich,This => Rich, This
    #
    text = missing_space_obj.sub(repl, text)

    for word in text.split():
        word = word.strip()
        has_punctuation = True in [ch in string.punctuation for ch in word]
        if word.isalpha() and not has_punctuation:
            #word = auto_correction(word, dictionary)
            clean_word = word.lower()
            clean_word = clean_word.translate(translator)
            if clean_word not in dictionary and clean_word not in string.punctuation:
                segments = segment(word)
                if len(known(segments)) == len(segments):
                    orig_case_segments = retain_case(word, segments)
                    word_segmented_text += " ".join(orig_case_segments)
                else:
                    word = auto_correction(word, dictionary)
                    word_segmented_text += word
            else:
                word_segmented_text += word

        else:
            word_segmented_text += word

        word_segmented_text += ' '

    word_segmented_text = word_segmented_text.strip()
    return word_segmented_text


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
                        default='../../Sample_Resources/Sample_Comments_CSVs/comments_csv_sample.csv',
                        #default = '/Users/vkolhatk/Data/GnM_CSVs/intermediate_csvs/new_comments_preprocessed_with_duplicates.csv',
                        #default='/Users/vkolhatk/Data/GnM_CSVs/intermediate_csvs/old_comments.csv',
                        help="the input csv file")

    parser.add_argument('--output_csv', '-o', type=str, dest='output_csv', action='store',
                        default='../../Sample_Resources/Sample_Comments_CSVs/comments_csv_sample_preprocessed.csv',
                        #default='/Users/vkolhatk/Data/GnM_CSVs/intermediate_csvs/new_comments1_preprocessed.csv',
                        #default='/Users/vkolhatk/Data/GnM_CSVs/intermediate_csvs/new_comments_preprocessed_with_duplicates_preprocessed.csv',
                        #default='/Users/vkolhatk/Data/GnM_CSVs/intermediate_csvs/old_comments_preprocessed.csv',
                        help="the output csv file")

    parser.add_argument('--column_to_preprocess', '-c', type=str, dest='column_name', action='store',
                        default='text',
                        help="the column to preprocess")

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
    dictionary = read_dictionary()

    start = timer()
    print('Start time: ', start)
    cores = cpu_count()
    partitions = cores
    df = pd.read_csv(args.input_csv)
    df_processed = parallelize(df, run_normalize)
    cols = ['article_id','comment_counter','comment_id','text','text_preprocessed','reactions','post_time','author','replies']
    df_processed.to_csv(args.output_csv, columns=cols, index=False)
    print('Output csv written: ', args.output_csv)
    end = timer()

    print('Total time taken: ', end-start)

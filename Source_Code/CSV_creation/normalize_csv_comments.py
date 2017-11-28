__author__ = 'Varada Kolhatkar'
import argparse, sys, os, glob, ntpath, pprint, codecs, re, csv
import pandas as pd
import wordsegment
from wordsegment import segment
from autocorrect import spell
from autocorrect import known

import string


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

def word_segmentation(text, dictionary):
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
    text = text.strip()
    missing_space_obj = re.compile(r'(?P<prev_word> \w{3,25}[.,?!;])(?P<next_word>(\w+))')

    def repl(m):
        return m.group('prev_word') + ' ' + m.group('next_word')

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

def normalize(input_csv, output_csv, column, dictionary):
    '''
    :param input_csv:
    :param output_csv:
    :param column:
    :param dictionary:
    :return:
    '''
    df = pd.read_csv(input_csv)
    df[column + '_preprocessed'] = df[column].apply(word_segmentation, args = ([dictionary]))
    df.to_csv(output_csv)
    print('Output csv written: ', output_csv)

def get_arguments():
    parser = argparse.ArgumentParser(description='Write csv files for crowd annotation')
    parser.add_argument('--input_csv', '-i', type=str, dest='input_csv', action='store',
                        default='../../Sample_Resources/Sample_Comments_CSVs/comments_csv_sample.csv',
                        help="the input csv file")

    parser.add_argument('--output_csv', '-o', type=str, dest='output_csv', action='store',
                        default='../../Sample_Resources/Sample_Comments_CSVs/comments_csv_sample_preprocessed.csv',
                        help="the output csv file")

    parser.add_argument('--column_to_preprocess', '-c', type=str, dest='column_name', action='store',
                        default='comment2',
                        help="the column to preprocess")

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = get_arguments()
    print(args)
    dictionary = read_dictionary()

    normalize(args.input_csv, args.output_csv, args.column_name, dictionary)




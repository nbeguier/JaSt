#!/usr/bin/python

# Standard
import argparse
import sys

# JaSt lib
import utility
import classifier
import static_analysis
from is_js import is_js_file

# Debug
# from pdb import set_trace as st

def parsing_commands():
    """
        Creation of an ArgumentParser object, holding all the information necessary to parse
        the command line into Python data types.

        -------
        Returns:
        - ArgumentParser such as:
          * js_dirs=arg_obj['d'],
          * labels_d=arg_obj['l'],
          * js_files=arg_obj['f'],
          * labels_f=arg_obj['lf'],
          * model=arg_obj['m'],
          * threshold=arg_obj['th'],
          * tolerance=arg_obj['t'][0],
          * n=arg_obj['n'][0].
          A more thorough description can be obtained:
            >$ python3 <path-of-clustering/classifier.py> -help
    """

    parser = argparse.ArgumentParser(description='Given a list of directory or file paths,\
    detects the malicious JS inputs.')

    parser.add_argument('--d', metavar='DIR', type=str, nargs='+',
                        help='directories containing the JS files to be analyzed')
    parser.add_argument('--l', metavar='LABEL', type=str, nargs='+',
                        choices=['benign', 'malicious', '?'],
                        help='labels of the JS directories to evaluate the model from')
    parser.add_argument('--f', metavar='FILE', type=str, nargs='+', help='files to be analyzed')
    parser.add_argument('--lf', metavar='LABEL', type=str, nargs='+',
                        choices=['benign', 'malicious', '?'],
                        help='labels of the JS files to evaluate the model from')
    parser.add_argument('--m', metavar='MODEL', type=str, nargs=1,
                        help='path of the model used to classify the new JS inputs '
                             + '(see >$ python3 <path-of-clustering/learner.py> -help) '
                             + 'to build a model)')
    parser.add_argument('--th', metavar='THRESHOLD', type=float, nargs=1, default=[0.29],
                        help='threshold over which all samples are considered malicious')
    utility.parsing_commands(parser)

    return vars(parser.parse_args())

OPTS = parsing_commands()
JAVASCRIPT = OPTS['f'][0]
MODEL = OPTS['m'][0]
TMPFILENAME = '/tmp/.tmp.js'

def get_malicious_score(js):
    """
        Classification of the sub-javascript
    """
    names, attributes, labels = static_analysis.main_analysis \
    (js_files=[js], js_dirs=OPTS['d'], labels_files=OPTS['lf'], labels_dirs=OPTS['l'], \
        n=OPTS['n'][0], tolerance=OPTS['t'][0], dict_not_hash=OPTS['dnh'][0])
    if not names:
        return 0
    _, labels_predicted_proba = classifier.test_model(names, labels, attributes, \
        model=MODEL, print_res=False, print_score=False)
    malicious_proba = int(labels_predicted_proba[0][1]*100)
    return malicious_proba

def main():
    """
        Main function
    """
    js = open(JAVASCRIPT, 'r')
    copy = open(TMPFILENAME, 'w+')
    line = js.readline()
    n = 1
    begin_line = n
    while line:
        copy.write(str(line))
        copy.close()
        if is_js_file(TMPFILENAME) == 0:
            score = get_malicious_score(TMPFILENAME)
            print('Line {} to {}: {}%'.format(begin_line, n, score))
            begin_line = n + 1
            copy = open(TMPFILENAME, 'w+')
        else:
            copy = open(TMPFILENAME, 'a+')
        line = js.readline()
        n += 1
    js.close()

if __name__ == '__main__':
    main()

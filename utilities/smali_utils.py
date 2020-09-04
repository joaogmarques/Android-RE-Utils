import argparse
import os
import sys
import re
from colorama import init, Fore


def get_dir_files(dir):
    fname = []
    for root, d_names, f_names in os.walk(dir):
        for f in f_names:
            fname.append(os.path.join(root, f))
    if not fname:
        return dir
    return fname


def print_regex_find(fname, reg):
    file = open(fname, 'r')
    for line in file:
        matches = reg.search(line)
        if matches:
            line_highlight = re.sub(reg, Fore.RED + r'\g<0>' + Fore.RESET, line)
            print('{}: {}'.format(fname, line_highlight), end='')
    file.close()


def find_class(jclass, dir):
    fname = get_dir_files(dir)
    r = str.replace(jclass, '$', '\$')
    rex = '\.class .*L{};'.format(r)
    reg = re.compile(rex, re.IGNORECASE)
    if type(fname) is str:
        print_regex_find(fname, reg)
    else:
        for file in fname:
            print_regex_find(file, reg)


def find_super(jsuper, dir):
    fname = get_dir_files(dir)
    r = str.replace(jsuper, '$', '\$')
    rex = '\.super .*L{};'.format(r)
    reg = re.compile(rex, re.IGNORECASE)
    if type(fname) is str:
        print_regex_find(fname, reg)
    else:
        for file in fname:
            print_regex_find(file, reg)


def find_interface(jinterface, dir):
    fname = get_dir_files(dir)
    r = str.replace(jinterface, '$', '\$')
    rex = '\.interface .*L{};'.format(r)
    reg = re.compile(rex, re.IGNORECASE)
    if type(fname) is str:
        print_regex_find(fname, reg)
    else:
        for file in fname:
            print_regex_find(file, reg)


def find_all(pattern, dir):
    fname = get_dir_files(dir)
    r = str.replace(pattern, '$', '\$')
    reg = re.compile(r, re.IGNORECASE)
    if type(fname) is str:
        print_regex_find(fname, reg)
    else:
        for file in fname:
            print_regex_find(file, reg)


def find_from_file(file_name, dir):
    f = open(file_name, 'r')
    for line in f:
        print('\nResults for String: {}'.format(line))
        find_all(line.strip(), dir)
        print('===================================================')
    f.close()


if __name__ == '__main__':

    init()

    my_parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                        description='Smali files utilities.\n\nThe search system works with '
                                                    'regex so for searches including '
                                                    'special characters don\'t forget to '
                                                    'escape them.\nExample: '
                                                    'smali_utils.py -a '
                                                    'class.example\\$1 smali/',
                                        epilog='EXAMPLES:\n\n'
                                               'smali_utils.py -c myapp.Activity smali/\n\n'
                                               'smali_utils -s android.app.Application smali/\n\n'
                                               'smali_utils -a sendTextMessage smali/\n\n'
                                               'smali_utils -f search.txt smali/')
    my_parser.add_argument('-c', '--class', dest='jclass', nargs=2, metavar=('<class>', '<dir>'),
                           help='search for java class in dir')
    my_parser.add_argument('-s', '--super', dest='jsuper', nargs=2, metavar=('<super>', '<dir>'),
                           help='search for super class in dir')
    my_parser.add_argument('-i', '--interface', dest='jinterface', nargs=2, metavar=('<interface>', '<dir>'),
                           help='search for interface implementation of class in dir')
    my_parser.add_argument('-a', '--all', dest='all', nargs=2, metavar=('<pattern>', '<dir>'),
                           help='search for String pattern in all smali in dir')
    my_parser.add_argument('-f', '--input-file', dest='input_file', nargs=2, metavar=('<input_file>', '<dir>'),
                           help='reads Strings from file and searches them in all smali in dir')

    if not len(sys.argv) > 1:
        my_parser.print_help()
        my_parser.exit()

    args = my_parser.parse_args()
    jclass = args.jclass
    jsuper = args.jsuper
    jinterface = args.jinterface
    all = args.all
    input_file = args.input_file
    if jclass:
        find_class(jclass[0], jclass[1])
    elif jsuper:
        find_super(jsuper[0], jsuper[1])
    elif jinterface:
        find_interface(jinterface[0], jinterface[1])
    elif all:
        find_all(all[0], all[1])
    elif input_file:
        find_from_file(input_file[0], input_file[1])

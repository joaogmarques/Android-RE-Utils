import argparse
import os
import sys
import re
from colorama import init, Fore

whitelist_filename = ''


def get_dir_files(dir):
    fname = []
    for root, d_names, f_names in os.walk(dir):
        for f in f_names:
            fname.append(os.path.join(root, f))
    if not fname:
        return dir
    return fname


def print_regex_find(fname, reg):
    if whitelist_filename != '':
        with open(whitelist_filename) as f:
            lines = f.readlines()
            for line_f in lines:
                if line_f.strip() in fname.strip():
                    return
    try:
        file = open(fname, 'r')
        for line in file:
            # matches = re.findall(reg, line) this is slow as hell
            matches = reg.search(line)
            if matches:
                line_highlight = re.sub(reg, Fore.RED + r'\g<0>' + Fore.RESET, line)
                print('{}: {}'.format(fname, line_highlight), end='')
    except:
        print("[-] Error on handling file {}.".format(file))
    file.close()


def print_regex_find_file(results, keys, fname, pattern_lists):
    file = open(fname, 'r')
    if whitelist_filename != '':
        with open(whitelist_filename) as f:
            if f.read() in fname:
                return
    for line in file:
        i = 0
        for reg in pattern_lists:
            matches = reg.search(line)
            if matches:
                line_highlight = re.sub(reg, Fore.RED + r'\g<0>' + Fore.RESET, line)
                results[keys[i]].append('{}: {}'.format(fname, line_highlight))
            i += 1
    file.close()


def find_class(jclass, dir):
    fname = get_dir_files(dir)
    r = str.replace(jclass, '$', '\$')
    rex = '\.class .*L.*{};'.format(r)
    reg = re.compile(rex, re.IGNORECASE)
    if type(fname) is str:
        print_regex_find(fname, reg)
    else:
        for file in fname:
            print_regex_find(file, reg)


def find_super(jsuper, dir):
    fname = get_dir_files(dir)
    r = str.replace(jsuper, '$', '\$')
    rex = '\.super .*L.*{};'.format(r)
    reg = re.compile(rex, re.IGNORECASE)
    if type(fname) is str:
        print_regex_find(fname, reg)
    else:
        for file in fname:
            print_regex_find(file, reg)


def find_interface(jinterface, dir):
    fname = get_dir_files(dir)
    r = str.replace(jinterface, '$', '\$')
    rex = '\.interface .*L.*{};'.format(r)
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
    mylist = [tuple(map(str, i.split(':', 1))) for i in f]
    for type, line in mylist:
        print('\nOption: {}\nResults for String: {}'.format(type, line.strip()))
        if type == '-a':
            find_all(line.strip(), dir)
        elif type == '-s':
            find_super(line.strip(), dir)
        elif type == '-i':
            find_interface(line.strip(), dir)
        elif type == '-c':
            find_class(line.strip(), dir)
        print('\n===================================================')
    f.close()


def find_from_file_v2(file_name, dir):
    pattern_list = []
    keys = []
    res = {}
    f = open(file_name, 'r')
    for line in f:
        r = str.replace(line.strip(), '$', '\$')
        reg = re.compile(r, re.IGNORECASE)
        pattern_list.append(reg)
        keys.append(line.strip())
        res[line.strip()] = []
    f.close()

    fname = get_dir_files(dir)
    if type(fname) is str:
        print_regex_find_file(res, keys, fname, pattern_list)
    else:
        for file in fname:
            print_regex_find_file(res, keys, file, pattern_list)

    for k, v in res.items():
        print('\nResults for String: {}\n'.format(k))
        for values in v:
            print(values, end='')
        print('===================================================')


def search_in_dir(src_dir, dir):
    for subdir, dirs, files in os.walk(src_dir):
        for filename in files:
            filepath = subdir + os.sep + filename
            print('\nParsing file: {}\n'.format(filename))
            find_from_file(filepath, dir)


def convert_to_dict(fname, keyword, delim):
    d = dict()
    file = open(fname, 'r')
    key = ""
    for l in file:
        line = l.strip()
        if line.startswith(keyword):
            key = line
            d[key] = []
        elif line != delim and line != '':
            d[key].append(line)
    for key, value in d.items():
        print('{} = {}'.format(key, value))


def find_encrypted_strings(pattern, dir):
    fname = get_dir_files(dir)
    if type(fname) is str:
        print_encrypted_find(fname, pattern)
    else:
        for file in fname:
            print_encrypted_find(file, pattern)


def print_encrypted_find(fname, method):
    try:
        file = open(fname, 'r')
        lines = file.readlines()
        i = 0
        while i < len(lines):
            l = lines[i].strip()
            if method in l:
                # get parameters received by the method call
                x = l.find('{')
                z = l.find('}')
                encrypted_params = l[x + 1:z]
                encrypted_vars = encrypted_params.split(',')
                for encrypted_var in encrypted_vars:
                    # create regex pattern to find the parameter value set
                    pattern = "const.* " + encrypted_var.strip() + ",.*"
                    r = str.replace(pattern, '$', '\$')
                    reg2 = re.compile(r, re.IGNORECASE)
                    y = i - 1
                    while y >= 0:
                        l2 = lines[y].strip()
                        matches_2 = reg2.search(l2)
                        if matches_2:
                            encrypted_string = l2.split('"')[1]
                            print(encrypted_string)
                            break
                        y -= 1
            i += 1
    except:
        print("[-] Error on handling file {}.".format(file))
    file.close()


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
                                               'smali_utils -f spyware_keywords.txt smali/')
    my_parser.add_argument('-c', '--class', dest='jclass', nargs=2, metavar=('<class>', '<dir>'),
                           help='search for java class in dir')
    my_parser.add_argument('-s', '--super', dest='jsuper', nargs=2, metavar=('<super>', '<dir>'),
                           help='search for super class in dir')
    my_parser.add_argument('-i', '--interface', dest='jinterface', nargs=2, metavar=('<interface>', '<dir>'),
                           help='search for interface implementation of class in dir')
    my_parser.add_argument('-a', '--all', dest='all', nargs=2, metavar=('<pattern>', '<dir>'),
                           help='search for String pattern in all smali in dir')
    my_parser.add_argument('-f', '--input-file', dest='input_file', nargs=2, metavar=('<input_file>', '<dir>'),
                           help='reads pairs [option:string_to_search] from file in smali in dir. Example: -a:sendTextMessage')
    my_parser.add_argument('-d', '--dir', dest='dir', nargs=2, metavar=('<files_dir>', '<dir>'),
                           help='reads pairs [option:string_to_search] from all files in the source dir in smali in dir.')
    my_parser.add_argument('-w', '--whitelist', dest='w', nargs=1, metavar=('<whitelist_file>'),
                           help='remove results that are in files with names that are contained in the whitelist file')
    my_parser.add_argument('-C', '--convert', dest='convert', nargs=3,
                           metavar=('<convert_file>', '<keyword>', 'delimiter'),
                           help='file to convert to dictionary, keys start with keyword and delimiter will be the delimiter between values and new key.')
    my_parser.add_argument('-e', '--encrypted', dest='encrypted', nargs=2,
                           metavar=('<decrypting_method>', '<smali_dir>'),
                           help='returns strings used as parameter in a particular method. Usefull to get all encrypted Strings from a specific decrypting method.')

    if not len(sys.argv) > 1:
        my_parser.print_help()
        my_parser.exit()

    args = my_parser.parse_args()
    jclass = args.jclass
    jsuper = args.jsuper
    jinterface = args.jinterface
    all = args.all
    input_file = args.input_file
    source_dir = args.dir
    convert = args.convert
    encrypted_strings = args.encrypted

    if args.w:
        if os.path.isfile(args.w[0]):
            whitelist_filename = args.w[0]
        else:
            print("[-] The whitelist file was not found. The results will not consider this flag.")

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
    elif source_dir:
        search_in_dir(source_dir[0], source_dir[1])
    elif convert:
        convert_to_dict(convert[0], convert[1], convert[2])
    elif encrypted_strings:
        find_encrypted_strings(encrypted_strings[0], encrypted_strings[1])
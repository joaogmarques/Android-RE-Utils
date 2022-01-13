import argparse
import os
import sys
import re
from colorama import init, Fore
from glob import glob

java_types_regex = {
    "J": "const-wide {0}, [-\w]+",
    "Ljava/lang/String": "const-string {0}, \".*\""
}
whitelist_filename = ''
do_regex = False
total_params_size = 0
params_types = []


def get_smali_from_dir(dir):
    return [y for x in os.walk(dir) for y in glob(os.path.join(x[0], '*.smali'))]


# this will return the total number of parameters that the encryption method has. The registers are 32 bit. 64-bit
# type (Long and Double type) require two registers to be represented but the first register contains the actual value
def get_total_params(method_call):
    global params_types
    global total_params_size
    if total_params_size == 0:
        result = re.search('\((.*)\)', method_call)
        f = result.group(1).split(';')
        params_types = list(filter(None, f))
        total_params_size = len(params_types)
    return total_params_size


def search_string_to_regex(search, rex):
    if not do_regex:
        pattern = re.escape(search)
    else:
        pattern = search
    r = rex.format(pattern)
    reg = re.compile(r, re.IGNORECASE)
    return reg


def print_regex_find(fname, reg):
    try:
        if whitelist_filename != '':
            with open(whitelist_filename) as f:
                lines = f.readlines()
                for line_f in lines:
                    if line_f.strip() in fname.strip():
                        return
        file = open(fname, 'r')
        for line in file:
            matches = reg.search(line)
            if matches:
                line_highlight = re.sub(reg, Fore.RED + r'\g<0>' + Fore.RESET, line)
                print('{}: {}'.format(fname, line_highlight), end='')
    except KeyboardInterrupt:
        sys.exit(1)
    except:
        print("[-] Error on handling file {}.".format(file))
        print(sys.exc_info()[0])
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
    fname = get_smali_from_dir(dir)
    rex = '\.class .*L.*{0};'
    reg = search_string_to_regex(jclass, rex)
    if type(fname) is str:
        print_regex_find(fname, reg)
    else:
        for file in fname:
            print_regex_find(file, reg)


def find_super(jsuper, dir):
    fname = get_smali_from_dir(dir)
    rex = '\.super .*L.*{0};'
    reg = search_string_to_regex(jsuper, rex)
    if type(fname) is str:
        print_regex_find(fname, reg)
    else:
        for file in fname:
            print_regex_find(file, reg)


def find_interface(jinterface, dir):
    fname = get_smali_from_dir(dir)
    rex = '\.interface .*L.*{0};'
    reg = search_string_to_regex(jinterface, rex)
    if type(fname) is str:
        print_regex_find(fname, reg)
    else:
        for file in fname:
            print_regex_find(file, reg)


def find_all(pattern, dir):
    fname = get_smali_from_dir(dir)
    reg = search_string_to_regex(pattern, "{0}")
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
    all_smali = get_smali_from_dir(dir)
    reg = search_string_to_regex(pattern, "{0}")
    if not all_smali:
        print_encrypted_find(dir, reg)
    else:
        for file in all_smali:
            print_encrypted_find(file, reg)


def print_encrypted_find(fname, method):
    try:
        file = open(fname, 'r')
        lines = file.readlines()
        i = 0
        while i < len(lines):
            l = lines[i].strip()
            matches = method.search(l)
            if matches:
                # get parameters received by the method call
                x = l.find('{')
                z = l.find('}')
                encrypted_params = l[x + 1:z]
                encrypted_vars = encrypted_params.split(',')
                index = 0
                size = get_total_params(l)
                while index < size:
                    encrypted_var = encrypted_vars[index]
                    pattern = java_types_regex[params_types[index]].format(encrypted_var)
                    index += 1
                    reg2 = re.compile(pattern, re.IGNORECASE)
                    y = i - 1
                    while y >= 0:
                        l2 = lines[y].strip()
                        matches_2 = reg2.search(l2)
                        if matches_2:
                            encrypted_string = l2.split(',')[1]
                            print(encrypted_string.strip().strip('\"'))
                            break
                        y -= 1
            i += 1
    except KeyboardInterrupt:
        sys.exit(1)
    except:
        print("[-] Error on handling file {}.".format(file))
        print(sys.exc_info()[0])
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
                                               'smali_utils.py -s android.app.Application smali/\n\n'
                                               'smali_utils.py -a sendTextMessage smali/\n\n'
                                               'smali_utils.py -Ea "https?://.*\.example\.com/.*" smali/\n\n'
                                               'smali_utils.py -f spyware_keywords.txt smali/\n\n'
                                               'smali_utils.py -e "Lmy/app/Decrypt;->decrypt(Ljava/lang/String;)Ljava/lang/String;" smali/')
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
                           help='acts as flag -f but reads multiple files from a directory')
    my_parser.add_argument('-w', '--whitelist', dest='w', nargs=1, metavar=('<whitelist_file>'),
                           help='remove results that are in files with names that are contained in the whitelist file')
    my_parser.add_argument('-C', '--convert', dest='convert', nargs=3,
                           metavar=('<convert_file>', '<keyword>', 'delimiter'),
                           help='file to convert to dictionary, keys start with keyword and delimiter will be the delimiter between values and new key.')
    my_parser.add_argument('-e', '--encrypted', dest='encrypted', nargs=2,
                           metavar=('<decrypting_method>', '<smali_dir>'),
                           help='returns data used as parameter in a particular method. Usefull to get all encrypted data from a specific decrypting method.')
    my_parser.add_argument('-E', dest='regex', action='store_true',
                           help='input used as regex.')
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
    r = args.regex

    if args.w:
        if os.path.isfile(args.w[0]):
            whitelist_filename = args.w[0]
        else:
            print("[-] The whitelist file was not found. The results will not consider this flag.")

    do_regex = r
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

import argparse
import sys


def xor_file_with_key(input_file, key):
    f = open(input_file, 'rb')
    s = f.read()
    f.close()

    key_b = key.encode('utf-8')
    g = open('decrypted.apk', 'wb')

    for i in range(len(s)):
        g.write(bytes([s[i] ^ key_b[i % len(key_b)]]))

    g.close()


if __name__ == '__main__':

    my_parser = argparse.ArgumentParser(description='Swiss knife utilities')
    my_parser.add_argument('-f', '--xor-file', dest='xor_file', nargs=2, metavar=('<input_filename>', '<key>'),
                           help='create new file \'decrypted.apk\' as a result of xor of file with key.')

    if not len(sys.argv) > 1:
        my_parser.print_help()
        my_parser.exit()

    args = my_parser.parse_args()
    xor_file = args.xor_file
    if xor_file:
        xor_file_with_key(xor_file[0], xor_file[1])
        print('XOR decrypt complete')

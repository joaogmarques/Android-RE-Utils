import argparse
import sys
import base64

output_file = 'decrypted'
read_all = False
pair = False
delim = []


def _read_file_bytes(input_file):
    f = open(input_file, 'rb')
    s = f.read()
    f.close()
    return s


def _read_file_lines(input_file):
    f = open(input_file, 'rb')
    s = f.readlines()
    return s


def _read_file(input_file):
    if not read_all:
        lines = _read_file_lines(input_file)
    else:
        lines = [_read_file_bytes(input_file)]
    return lines


def _write_to_file(data):
    g = open(output_file, 'wb')
    for value in data:
        g.write(bytes([value]))
    g.close()


def _base64_decode(data):
    return base64.b64decode(data)


def _get_delim():
    global delim
    if delim:
        return delim
    for bytes in ' : '.encode('utf-8'):
        delim.append(bytes)
    return delim


def _xor_data(data, key):
    key_b = key.encode('utf-8')
    x = []
    for i in range(len(data)):
        x.append(data[i] ^ key_b[i % len(key_b)])
    return x


def _get_pair_list(s, delim):
    pair_list = []
    if pair:
        i = 0
        while i < len(s) - 1:
            pair_list.append(s[i])
            i += 1
        pair_list.extend(delim)
    return pair_list


def base64_decode(input_file):
    lines = _read_file(input_file)
    decrypted = []
    delim = _get_delim()
    index = 0
    for s in lines:
        decrypted.extend(_get_pair_list(s, delim))
        decrypted.extend(_base64_decode(s))
        if not read_all:
            # 10 is the int value for \n
            decrypted.append(10)
        index += 1
    _write_to_file(decrypted)


def string_fog(input_file, key):
    lines = _read_file(input_file)
    decrypted = []
    delim = _get_delim()
    index = 0
    for s in lines:
        b64_decoded_bytes = _base64_decode(s)
        decrypted.extend(_get_pair_list(s, delim))
        decrypted.extend(_xor_data(b64_decoded_bytes, key))
        if not read_all:
            # 10 is the int value for \n
            decrypted.append(10)
        index += 1
    _write_to_file(decrypted)


def xor_file(input_file, key):
    lines = _read_file(input_file)
    decrypted = []
    delim = _get_delim()
    index = 0
    for s in lines:
        decrypted.extend(_get_pair_list(s, delim))
        decrypted.extend(_xor_data(s, key))
        if not read_all:
            # 10 is the int value for \n
            decrypted.append(10)
        index += 1
    _write_to_file(decrypted)


if __name__ == '__main__':
    my_parser = argparse.ArgumentParser(description='Decrypt utilities')
    my_parser.add_argument('-x', '--xor', dest='xor', nargs=2, metavar=('<input_filename>', '<key>'),
                           help='Applies XOR decryption to file. Default output file \'{0}\''.format(output_file))
    my_parser.add_argument('--string-fog', dest='fog', nargs=2, metavar=('<input_filename>', '<key>'),
                           help='StringFog decryption (aka Base64+XOR). Default output file \'{0}\''.format(
                               output_file))
    my_parser.add_argument('-b', '--base64', dest='b64', nargs=1, metavar='<input_filename>',
                           help='Base64 decodes a file. Default output file \'{0}\''.format(output_file))
    my_parser.add_argument('-o', '--output', dest='output', nargs=1, metavar='<output_filename>',
                           help='Output file that gets created. Default file is \'{0}\''.format(output_file))
    my_parser.add_argument('-A', '--All', dest='all', action='store_true',
                           help='Decrypts input file contents as a unique line. Default behavior is to decrypt line '
                                'by line')
    my_parser.add_argument('-p', '--pair', dest='pair', action='store_true',
                           help='instead of only decrypting, it creates a pair with the encrypted and respective '
                                'decrypted value')

    if not len(sys.argv) > 1:
        my_parser.print_help()
        my_parser.exit()

    args = my_parser.parse_args()
    xor = args.xor
    fog = args.fog
    output = args.output

    read_all = args.all
    pair = args.pair
    if output:
        output_file = output[0]
    if xor:
        xor_file(xor[0], xor[1])
        print('XOR decrypt complete')
    elif fog:
        string_fog(fog[0], fog[1])
        print('StringFog decrypt complete')
    print('Output file: {0}'.format(output_file))

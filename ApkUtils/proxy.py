#!/Library/Frameworks/Python.framework/Versions/3.8/bin/python3

import argparse
import os
import netifaces


def show_interfaces(family):
    print('Available IPs:')
    for interface in netifaces.interfaces():
        if bool(netifaces.ifaddresses(interface)):
            try:
                netifaces.ifaddresses(interface)[family]
            except:
                continue
            print("-----------\n" + interface)
            print(netifaces.ifaddresses(interface)[family][0]['addr'])


if __name__ == '__main__':

    # Create the parser
    my_parser = argparse.ArgumentParser(description='Change android device proxy settings.')
    my_parser.add_argument('-d', '--device', dest='device', type=str, metavar='<device_id>',
                           help='apply changes to the device id provided', default='')
    my_parser.add_argument('-s', '--set', dest='set', nargs='?',
                           help='set the proxy with <ip>:<port>')
    my_parser.add_argument('-u', '--unset', dest='unset', action='store_true',
                           help='unset the proxy')

    args = my_parser.parse_args()
    device = args.device
    set = args.set
    unset = args.unset

    d = __import__('get_devices')

    device = d.select_device(device)

    if unset:
        print('Unsetting proxy in device {}.'.format(device))
        os.system('adb -s {} shell settings put global http_proxy :0'.format(device))
    elif set or set is None:
        if set is None:
            show_interfaces(netifaces.AF_INET)
            set = input("Insert <IP:PORT> to set proxy: ")
        print('Setting proxy to {} in device {}'.format(set, device))
        os.system('adb -s {} shell settings put global http_proxy {}'.format(device, set))

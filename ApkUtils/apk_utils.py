#!/Library/Frameworks/Python.framework/Versions/3.8/bin/python3

import argparse
import os
import subprocess
import sys
# import aux

# def moduleNames(package):
#     folder = os.path.split(package.__file__)[0]
#     for name in os.listdir(folder):
#         if name.endswith(".py") and not name.startswith("__"):
#             yield name[:-3]
#
#
# def importSubmodules(package):
#     names = list(moduleNames(package))
#     m = __import__(package.__name__, globals(), locals(), names, 0)
#     return [getattr(m, name) for name in names]


if __name__ == '__main__':

    # Create the parser
    my_parser = argparse.ArgumentParser(description='Some useful utilities for APKs and device')
    my_parser.add_argument('-d', '--device', dest='device', type=str, metavar='<device_id>',
                           help='apply changes to the device id provided', default='')
    my_parser.add_argument('-r', '--root', dest='root', action='store_true',
                           help='start adb as root and launch a shell.')
    my_parser.add_argument('-s', '--shell', dest='shell', action='store_true',
                           help='launch shell of device.')
    my_parser.add_argument('-S', '--screenshot', dest='screenshot', action='store_true',
                           help='take a screenshot and save it in current dir.')
    my_parser.add_argument('-u', '--uninstall', dest='uninstall', type=str, metavar='<apk_file>',
                           help='uninstall give apk file')
    my_parser.add_argument('-i', '--install', dest='install', type=str, metavar='<apk>',
                           help='install given APK')
    my_parser.add_argument('-m', '--multiple-install', dest='multiple', type=str, metavar='<apks_dir>',
                           help='install APK from given dir with multiple files')

    if not len(sys.argv) > 1:
        my_parser.print_help()
        my_parser.exit()

    args = my_parser.parse_args()
    device = args.device
    screenshot = args.screenshot
    uninstall = args.uninstall
    multiple = args.multiple
    install = args.install
    root = args.root
    shell = args.shell

    d = __import__('get_devices')

    device = d.select_device(device)

    if screenshot:
        print('Taking screenshot from device {}.'.format(device))
        os.system('adb -s {} shell screencap -p /sdcard/screen.png && adb -s {} pull /sdcard/screen.png screen_$(date '
                  '+%s).png'.format(device, device))
    elif multiple:
        print('Installing multiple APKs in device {}'.format(device))
        permissions = input('Do you want to grant all runtime permissions preemptively? (y/n)')
        if permissions.casefold() == 'y':
            os.system('adb -s {} install-multiple -g {}/*.apk'.format(device, multiple))
        else:
            os.system('adb -s {} install-multiple {}/*.apk'.format(device, multiple))
    elif uninstall:
        print('Uninstalling the APK in device {}'.format(device))
        command = 'aapt dump badging ' + uninstall + ' | grep "package:\\ name" | awk -F"\'" \'{ print $2 }\''
        out = subprocess.Popen([command],
                               shell=True,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, )
        stdout, stderr = out.communicate()
        pkg = stdout.split()[0].decode()
        os.system('adb -s {} uninstall {}'.format(device, pkg))
    elif install:
        print('Installing the APK in device {}'.format(device))
        permissions = input('Do you want to grant all runtime permissions preemptively? (y/n)')
        if permissions.casefold() == 'y':
            os.system('adb -s {} install -g {}'.format(device, install))
        else:
            os.system('adb -s {} install {}'.format(device, install))
    elif root:
        print('Starting ADB as root and launching shell in device {}'.format(device))
        os.system('adb -s {} root'.format(device))
        os.system('adb -s {} shell'.format(device))
    elif shell:
        print('Launching shell in device {}'.format(device))
        os.system('adb -s {} shell'.format(device))

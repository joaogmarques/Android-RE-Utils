import subprocess


def get_devices():
    out = subprocess.Popen(['adb', 'devices'],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()
    device_list = stdout.split()
    devs = []
    if len(device_list) >= 6:
        i = 4
        while len(device_list) > i:
            devs.append(device_list[i].decode())
            i += 2
    return devs


def select_device(device):
    if not device:
        devices = get_devices()
        i = 0

        print('Available devices:\n')
        while len(devices) > i:
            print('{}) {}'.format(i, devices[i]))
            i += 1

        j = input('\nEnter the index of device to use:')
        dev = devices[int(j)]
        return dev
    else:
        return device

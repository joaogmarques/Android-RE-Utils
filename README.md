# Android-RE-Utils

Some utility scripts to simplify and acelerate Android RE process.

Feel free to add something up :)

## Usage

1. Each directory has its own `requirements.txt`, so install the necessary dependencies by using `pip install -r requirements.txt`.
2. Execute: `python3 script.py`

### ApkUtils

#### apk_utils.py

Has some shortcut commands to perform on the device, like take screenshot or open shell. Has other commands to install/uninstall apks or splitted apks.

#### proxy.py

Shortcut command to set/unset proxy IP:PORT on the device.

### utilities

#### decrypt.py 

Decryption commands, like XOR, StringFog or Base64.

#### smali_utils.py

Multiple commands to search stuff in the smali files. Locate Strings, Classes, API calls or Encrypted Strings.

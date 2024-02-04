import platform
import sys


def retTypeAndMachine():
    # Detect machine and ostype
    ostype = platform.system().lower()
    if ostype.find("cygwin") >= 0:  # Support cygwin x11
        ostype = "windows"
    machine = platform.machine().lower()
    if machine in ['aarch64_be', 'armv8b', 'armv8l']:
        machine = 'aarch64'
    if machine in ['i386', 'i686']:
        machine = 'x86'
    if machine == "amd64":
        machine = 'x86_64'
    if ostype == 'windows':
        if not machine == 'x86_64':
            sys.stderr.write("Error : Program on windows only support 64bit machine\n")
            return None
    if ostype == 'linux':
        if machine not in ['aarch64', 'arm', 'x86', 'x86_64']:
            sys.stderr.write("Error : Machine not support your device [%s]\n" % machine)
            return None
    return ostype.replace('windows', 'win'), machine

#!/usr/bin/env python3
import random
import functions
import sys
import Montgomery

#reads bytefile and returns a hex string
def read_from_file(filename, binary = True):
    mode = "rb"
    if (not binary):
        mode = "r"
    file = open(filename, mode = mode)
    content = file.read()
    file.close()
    if (binary):
        return content.hex()
    return content
#info should be a hex string
def write_to_file(info, filename):
    file = open(filename, "wb")
    file.write(bytes(bytearray.fromhex(info)))
    file.close()
    return

def main():
    user_input = list(sys.argv)[1:] 
    if (len(user_input) != 1):
        print("usage: msg_to_bin.py message_file")
    msg = str(read_from_file(user_input[0], False))
    print(msg)
    fileout = user_input[0].split(".")
    fileout[-1] = "bin"
    fileout = ".".join(fileout)
    write_to_file(msg, fileout)
    return

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
import functions
import sys

#reads bytefile and returns a hex string
def read_from_file(filename):
    file = open(filename, mode = "rb")
    content = file.read()
    file.close()
    return content.hex()

def main():
    user_input = list(sys.argv)[1:]      
    if (len(user_input) != 3):
        print("usage: verifyEd25519.py signature_list_file keys_file messages_file")
        return
    sig = read_from_file(user_input[0])
    pubKey = read_from_file(user_input[1])
    message = read_from_file(user_input[2])
    

    return

if __name__ == "__main__":
    main()
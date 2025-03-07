#!/usr/bin/env python3
import sys
import random
import functions
import Montgomery

def read_from_file(filename): #read as a plain text, hex values
    file = open(filename, mode = "r")
    content = file.read()
    file.close()
    return content

#info should be a hex string
def write_to_file(info, filename):
    file = open(filename, "w")
    for line in info:
        file.write(line + "\n")
    file.close()
    return

def Hash(to_hash, diff = "00", output_size = 32):
    to_hash = diff + to_hash #just to make hashes different
    out = bytes.fromhex(to_hash)
    out = bytearray(functions.hashlib.sha512(out).digest())

    #print(pkh.hex()[:64]) #public key hash, just put 32 bytes
    return out.hex()[:output_size * 2]

def main():
    args = list(sys.argv)[1:]

    #private keys are stored in lines, with \n splitting the (SK, s, PK, PKH)
    input_arg = list(sys.argv)[1:]
    if (input_arg != []):
        content = read_from_file(input_arg[0]).split("\n")
        sk = content[0]
    else:
        sk = random.randint(0, 2**256)
        sk = hex(sk)[2:].zfill(32)
    
    m = Montgomery.split_to_numbers(sk)
    m = Montgomery.decodeScalar25519(m)

    u = 9
    pk = Montgomery.ladder(m, Montgomery.Point(u, 1))
    pk = Montgomery.encodeUCoordinate(pk)

    ls = 256
    s = random.randint(0, 2**ls) #32 bytes
    s = hex(s)[2:].zfill(64) #64 entries
    #print(s)

    pkh = Hash(pk, "01", 32) #this is G1 

    print(pk)
    write_to_file([sk, s, pk, pkh], "test1_keygen.sk")    
    
    return

if __name__ == "__main__":
    main()



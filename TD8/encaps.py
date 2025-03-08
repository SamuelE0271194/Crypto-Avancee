#!/usr/bin/env python3
import sys
import random
import Montgomery
import functions

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

def encrypt(msg, pk, r):

    m = Montgomery.split_to_numbers(r)
    m = Montgomery.decodeScalar25519(m)
    u = 9
    c1 = Montgomery.ladder(m, Montgomery.Point(u, 1))
    c1 = Montgomery.encodeUCoordinate(c1) 

    pk_m = Montgomery.split_to_numbers(pk)
    pk_m = Montgomery.decodeUCoordinate(pk_m)
    
    shared = Montgomery.ladder(m, Montgomery.Point(pk_m, 1))
    shared = Montgomery.encodeUCoordinate(shared)

    c2 = int(msg, 16) ^ int(shared, 16) #just xoring the values
    c2 = hex(c2)[2:].zfill(64) #32 bytes
    #print("msg = " + msg)
    #print("shared = " + shared)
    #print("tail = " + c2)
    return c1 + c2

def main():
    args = list(sys.argv)[1:]
    if len(args) != 1:
        print("format : encaps.py public_key(32 bytes)")
        return
    
    pk = args[0]

    #generating random message 
    m_l = 256 #32 bytes
    msg = random.randint(0, 2**m_l) #32 bytes
    msg = hex(msg)[2:].zfill(64) #32 bytes, 64 entries

    pkh = Hash(pk, "01", 32)
    rk = Hash(pkh + msg, "02", 64) #32 bytes for r, 32 bytes for k
    
    r = rk[:64] #32 bytes 
    k = rk[64:]

    c = encrypt(msg, pk, r) #32 + 32 bytes

    K = Hash(c + k, "03", 16)
    
    print(c)
    print(K)

    return

if __name__ == "__main__":
    main()
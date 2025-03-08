#!/usr/bin/env python3
import sys
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

def encrypt(msg, pk, r): #r is the scalar to multiply the point by
    m = Montgomery.split_to_numbers(r)
    m = Montgomery.decodeScalar25519(m)
    u = 9
    #technically can ommit this computation here since c1 is not needed, but i'll leave it here since its a copy of the one in encaps
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
    if len(args) != 2:
        print("format : decaps.py Private_key(file) Ciphertext(hex)")
        return

    private_key = read_from_file(args[0]).split("\n")
    sk = private_key[0]
    s = private_key[1]
    pk = private_key[2]
    pkh = private_key[3]

    cipher = args[1]

    c1 = cipher[:64] #first 32 bits are the public key
    c2 = cipher[64:]

    m_original = encrypt(c2, c1, sk)
    m_original = m_original[64:]

    rk = Hash(pkh + m_original, "02", 64)
    r = rk[:64] 
    k = rk[64:] 

    k0 = Hash(cipher + k, "03", 16)
    k1 = Hash(cipher + s, "03", 16)

    c_check = encrypt(m_original, pk, r)
    if c_check == cipher:
        print(k0)
        #print("Good")
    else:
        print(k1)

    return

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
import functions
import sys

#a, b bit array
def multiexp(a, b, P, Q):
    return 1

def verify(signature, publickey, message):    
    
    base_pt = functions.Edwards25519Point.stdbase()
    R, Sraw = signature[:256//8], signature[256//8:]
    s = functions.from_le(Sraw)
    Q = bytes.fromhex(publickey)
    m = bytes.fromhex(message)

    h = functions.hashlib.sha512(R + Q + m)
    R = (functions.Edwards25519Point.stdbase() * s)
    R_check = multiexp(s, -h, base_pt, Q)

    return False



def main():

    return

if __name__ == "__main__":
    main()
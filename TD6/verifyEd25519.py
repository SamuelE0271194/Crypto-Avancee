#!/usr/bin/env python3
import functions
import sys

#a, b integers,
#  P,Q points from the functions in RFC
#   returns aP + bQ
def multiexp(a, b, P, Q, zero_pt):
    #a = list(bin(a)[2:])
    b = list(bin(b)[2:])
    T = [[zero_pt, Q], [P, P + Q]]
    R = zero_pt
    #if (len(a) > len(b)):
    #    b = [0 for i in range(len(a) - len(b))] + b
    #elif (len(b) > len(a)):
    #    a = [0 for i in range(len(b) - len(a))] + a
    while a > 0:
        if (a % 2) > 0:
            R = R + P
        P = P.double()
        a //= 2
    for i in range(len(a)):
        R = R + T[int(a[i])][int(b[i])]
        R = R.double()
        print(R.encode().hex())
    return R

def verify(signature, publickey, message):    
    
    base_pt = functions.Edwards25519Point.stdbase()
    sig = bytes.fromhex(signature)
    R, Sraw = sig[:256//8], sig[256//8:]
    s = functions.from_le(Sraw)
    pubkey = bytes.fromhex(publickey)
    Q = base_pt.decode(pubkey)
    m = bytes.fromhex(message)

    mod = functions.hexi("1000000000000000000000000000000014def9dea2f79cd65812631a5cf5d3ed")
    h = (-functions.from_le(functions.hashlib.sha512(R + pubkey + m).digest())) % mod
    R = base_pt.decode(R)
    print(R.encode().hex())
    R_temp = (base_pt * s)# + (Q * h)
    print(R_temp.encode().hex())
    R_check = multiexp(s, 0, base_pt, Q, base_pt.zero_elem())
    print(R_check.encode().hex())

    return R_check == R

#reads bytefile and returns a hex string
def read_from_file(filename):
    file = open(filename, mode = "rb")
    content = file.read()
    file.close()
    return content.hex()

def main():
    user_input = list(sys.argv)[1:]      
    if (len(user_input) != 3):
        print("usage: verifyEd25519.py signature_file public_key_file message_file")
        return
    sig = read_from_file(user_input[0])
    pubKey = read_from_file(user_input[1])
    message = read_from_file(user_input[2])
    
    if (verify(sig, pubKey, message)):
        print("ACCEPT")
    else:
        print("REJECT")

    return

if __name__ == "__main__":
    main()
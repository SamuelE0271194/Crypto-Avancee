#!/usr/bin/env python3
import sys
import verifyEd25519
import random
import functions

#a, b integers,
#  P,Q points from the functions in RFC
#   returns aP + bQ
def multiexp_batch(parsed_info, base_pt, zero_pt):
    for i in range(len(parsed_info)):
        parsed_info[i][0] = list(parsed_info[i][0])
        parsed_info[i][2] = list(parsed_info[i][2])
        parsed_info[i][3] = list(parsed_info[i][3])

    R = zero_pt
    for i in range(len(parsed_info[0][0])): #just running through the number of bits
        R = R.double()
        for j in range(len(parsed_info)):
            if parsed_info[j][0][i] == "1":
                R = R + parsed_info[j][1]
            if parsed_info[j][2][i] == "1":
                R = R + base_pt
            if parsed_info[j][3][i] == "1":
                R = R + parsed_info[j][4]
    return R

def verify_batch(info):    

    z = [1 for i in range(len(info))] 
    #z = [random.randint(0, 2**128) for i in range(len(info))]
    info_parsed = [] #info[i] = [zi, R(point), s, -h, Q(point)]
    #getting the max bit length (number of bits to pad everything to)
    num_bits = 0

    for i in range(len(info)):
        signature = read_from_file(info[i][0])
        publickey = read_from_file(info[i][1])
        message = read_from_file(info[i][2])

        base_pt = functions.Edwards25519Point.stdbase()
        sig = bytes.fromhex(signature)
        R, Sraw = sig[:256//8], sig[256//8:]
        s = functions.from_le(Sraw)
        pubkey = bytes.fromhex(publickey)
        Q = base_pt.decode(pubkey)
        m = bytes.fromhex(message)

        mod = functions.hexi("1000000000000000000000000000000014def9dea2f79cd65812631a5cf5d3ed") #order of base pt
        
        #already taking -h here
        h = (-functions.from_le(functions.hashlib.sha512(R + pubkey + m).digest())) % mod
        
        s_store = bin((s * z[i]) % mod)[2:]
        h_store = bin((h * z[i]) % mod)[2:]
        if len(s_store) > num_bits:
            num_bits = len(s_store)
        if len(h_store) > num_bits:
            num_bits = len(h_store)
        z_store = bin(-z[i] % mod)[2:]
        if len(z_store) > num_bits:
            num_bits = len(z_store)
        R = base_pt.decode(R)
        info_parsed.append([z_store, R, s_store, h_store, Q])

    #padding out all the "scalars" 
    for i in range(len(info)):
        info_parsed[i][0] = info_parsed[i][0].zfill(num_bits)
        info_parsed[i][2] = info_parsed[i][2].zfill(num_bits)
        info_parsed[i][3] = info_parsed[i][3].zfill(num_bits)

    #print(R.encode().hex())

    
    R_check = multiexp_batch(info_parsed, base_pt, base_pt.zero_elem())
    
    return R_check == base_pt.zero_elem()

#reads bytefile and returns a hex string
def read_from_file(filename, binary = True):
    mode = "r"
    if (binary):
        mode = "rb"
    file = open(filename, mode = mode)
    content = file.read()
    file.close()
    if (binary):
        return content.hex()
    return content

def main():
    user_input = list(sys.argv)[1:]      
    if (len(user_input) != 1):
        print("usage: batch.py batchfile")
        print("Ensure that files are in the current working directory")
        return
    info = read_from_file(user_input[0], False).split("\n")
    info = [line.split(" ") for line in info]

   # for i in range(len(info)):
        #sigTemp = read_from_file(info[i][0])
        #keyTemp = read_from_file(info[i][1])
        #msgTemp = read_from_file(info[i][2])

        #if not verifyEd25519.verify(sigTemp, keyTemp, msgTemp):
            #print("REJECT (Don't know which one)")
            #return
    
    verif = verify_batch(info)
    
    if verif:
        print("ACCEPT")
        return

    print("REJECT")

    return

if __name__ == "__main__":
    main()
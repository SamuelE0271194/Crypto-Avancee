#!/usr/bin/env python3
import random
import functions
import sys

#takes in private key and retunrs the corresponding public key
#private key here is 32 byte (in integer form)
def keygen(private = None):
    if private == None:
        private = random.randint(0, 2**256) #32 bytes
        private = hex(private)[2:].zfill(32) 
    #Take the private value here to be in le form
    private_bytes = bytes.fromhex(private)
    private_hashed = bytearray(functions.hashlib.sha512(private_bytes).digest())
    
    for i in range(0,3): #clamp the first 3
        private_hashed[i//8]&=~(1<<(i%8))
    private_hashed[254//8]|=1<<(254%8) #clamp the last bit
    for i in range(254+1,256): #clamp the last 2
        private_hashed[i//8]&=~(1<<(i%8))

    public = functions.from_le(private_hashed[:256//8]) #take the first 32 bytes    
    public = (functions.Edwards25519Point.stdbase() * public).encode()
    return (private, public.hex())

#info should be a hex string
def write_to_file(info, filename):
    file = open(filename, "wb")
    file.write(bytes(bytearray.fromhex(info)))
    file.close()
    return

def main():

    #keygen("4ccd089b28ff96da9db6c346ec114e0f5b8a319f35aba624da8cf6ed4fb8a6fb")
    #Above code should output 3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c 
    input_key = list(sys.argv)[1:]
    if (input_key != []):
        key_pair = keygen(input_key[0])
    else:
        key_pair = keygen()
    
    write_to_file(key_pair[0], "prefix.sk")
    #print(key_pair[0])
    #print(len(key_pair[0]))
    write_to_file(key_pair[1], "prefix.pk")
    return

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
import random
import functions
import sys
import Montgomery

#takes in private key and retunrs the corresponding public key
#private key here is 32 byte (in integer form)
def keygen(private = None,
           ed_a = -1, 
           ed_d = 37095705934669439343138083508754565189542113879843219016388785533085940283555,
           ed_p = 2**255 - 19):
    
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
    
    base_pt_ed = functions.Edwards25519Point.stdbase()
    ed_x = int.from_bytes(base_pt_ed.x.tobytes(256), byteorder="little")
    ed_y = int.from_bytes(base_pt_ed.y.tobytes(256), byteorder="little")
    ed_z = int.from_bytes(base_pt_ed.z.tobytes(256), byteorder="little")
    
    ed_point = Montgomery.Point(ed_x, ed_y, ed_z)
    public = multiply(public, ed_point, ed_a, ed_d, ed_p)
    
    public = public.y_to_le()
    return (private, public)

#takes in a point on an edwards curve, sends it to a montgomery curve 
#   multiple, then send back to the edwards curve
def multiply(s, ed_P, ed_a, ed_d, ed_prime):
    #converting the point on the ed curve to a point on a mont curve 
    mont_point, mont_A, mont_B = Montgomery.Ed_to_Mont(ed_a, ed_d, ed_P)
    #scalling the point
    scal_mont = Montgomery.ladder(s, mont_point, Montgomery.Curve(mont_A, mont_B, ed_prime))
    #converting back to an ed point
    ed_point_scal, dummy1, dummy2 = Montgomery.Mont_to_Ed(mont_A, mont_B, scal_mont)
    #dummy1 and dummy2 are ed_a and ed_d
    return ed_point_scal


#info should be a hex string
def write_to_file(info, filename):
    file = open(filename, "wb")
    file.write(bytes(bytearray.fromhex(info)))
    file.close()
    return

def main():

    #key_pair = keygen("4ccd089b28ff96da9db6c346ec114e0f5b8a319f35aba624da8cf6ed4fb8a6fb")
    #Above code should output 3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c 
    input_key = list(sys.argv)[1:]
    if (input_key != []):
        key_pair = keygen(input_key[0])
    else:
        key_pair = keygen()
    
    #print(public)
    write_to_file(key_pair[0], "prefix.sk")
    write_to_file(key_pair[1], "prefix.pk")
    return

if __name__ == "__main__":
    main()
#!/usr/bin/env python3

import functions
import sys
import keygen
import Montgomery

#message as a hex string
def sign(msg, private, public = None,
         ed_a = -1, 
         ed_d = 37095705934669439343138083508754565189542113879843219016388785533085940283555,
         ed_p = 2**255 - 19):

    private_key = bytes.fromhex(private)
    message = bytes.fromhex(msg)
                     #bytearray(functions.hashlib.sha512(private_bytes).digest())
    private_hashed = bytearray(functions.hashlib.sha512(private_key).digest())
    #clamping
    for i in range(0,3): #clamp the first 3
        private_hashed[i//8]&=~(1<<(i%8))
    private_hashed[254//8]|=1<<(254%8) #clamp the last bit
    for i in range(254+1,256): #clamp the last 2
        private_hashed[i//8]&=~(1<<(i%8))

    x = functions.from_le(private_hashed[:256//8]) #take the first 32 bytes    
    if (public == None):
        public_key = bytes.fromhex(keygen.keygen(private)[1])
    else:
        public_key = bytes.fromhex(public)

    mod = functions.hexi("1000000000000000000000000000000014def9dea2f79cd65812631a5cf5d3ed")

    y = private_hashed[256//8:] #tail
    r = y + message
    r = functions.from_le(functions.hashlib.sha512(r).digest()) % mod
    
    base_pt_ed = functions.Edwards25519Point.stdbase()
    ed_x = int.from_bytes(base_pt_ed.x.tobytes(256), byteorder="little")
    ed_y = int.from_bytes(base_pt_ed.y.tobytes(256), byteorder="little")
    ed_z = int.from_bytes(base_pt_ed.z.tobytes(256), byteorder="little")
    
    ed_point = Montgomery.Point(ed_x, ed_y, ed_z)
    R = multiply(r, ed_point, ed_a, ed_d, ed_p)
    R = bytearray.fromhex(R.y_to_le())

    # gotta transport the points on to a montgomery curve
    h = functions.from_le(functions.hashlib.sha512(R + public_key + message).digest()) % mod
    s = ((r + h * x) % mod).to_bytes(256//8, byteorder="little")

    return R + s 

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


#reads bytefile and returns a hex string
def read_from_file(filename):
    file = open(filename, mode = "rb")
    content = file.read()
    file.close()
    return content.hex()
#info should be a hex string
def write_to_file(info, filename):
    file = open(filename, "wb")
    file.write(bytes(bytearray.fromhex(info)))
    file.close()
    return

def main():
    user_input = list(sys.argv)[1:] 
    if (len(user_input) < 2 or len(user_input) > 3):
        print("usage: signEd25519.py message private.sk public.pk(optional)")
    message = str(read_from_file(user_input[0]))
    private_key = str(read_from_file(user_input[1]))
    public_key = None
    if (len(user_input) == 3):
        public_key = str(read_from_file(user_input[2]))

    out = sign(message, private_key, public_key)
    print(out.hex())
    write_to_file(out.hex(), "signature.bin")
    return out

if __name__ == "__main__":
    main()

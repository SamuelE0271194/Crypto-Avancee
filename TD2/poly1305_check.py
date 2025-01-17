#!/usr/bin/env python3
import sys

#hex to bytes
def hex_to_byt(hex_list):
    byt_list = []
    for x in hex_list:
        byt_store = bin(int(x, 16))[2:].zfill(8)
        byt_list.append(byt_store)
    #byt_list = byt_list[::-1]
    return byt_list

#byte to hex
def byt_to_hex(byt_list):
    hex_list = []
    for x in byt_list:
        hex_store = hex(int(x,2)).split("x")[-1]
        if (len(hex_store) < 2):
            hex_store = "0" + hex_store
        hex_list.append(hex_store)
    return hex_list

#reads file as bits, then returns a list of bytes, should be a txt
def read_file_byt(filename):
    f = open(filename)
    content = f.read()
    f.close()
    
    out = [bin(x)[2:].zfill(8) for x in bytearray(content, 'utf-8')]
    return out

#input rs, r is 32 bytes, and s is 32 bytes, so 64 byte input
# output r and s as seperate lists
def read_rs(rs):
    r = rs[:16] 
    s = rs[16:]
    
    #clamp r
    for i in [3, 7, 11, 15]:
        r[i] = "0000" + r[i][4:]
    for i in [4, 8, 12]:
        r[i] = r[i][:6] + "00"

    r_out = bytes_to_number(r[::-1])
    s_out = bytes_to_number(s[::-1])

    return r_out, s_out

# input is the message in bytes, splits into 16 byte chunks
def split_msg(message):
    split = len(message)//16
    out = [message[(i*16) : ((i+1)*16)] for i in range(split)]
    if (len(message)%16 != 0):
        out.append(message[(split * 16):])
    return out

#takes in a chunk (list of bytes) (max 16 bytes) and converts it into a number
def bytes_to_number(chunk):
    in_bits = "".join(chunk)
    return int(in_bits, 2)

#change number into list of bytes
def number_to_bytes(number):
    in_bits = bin(number).split("b")[-1]
    size = len(in_bits) % 8
    if (size != 0):
        size = len(in_bits) + 8 - size
    in_bits = in_bits.zfill(size)
    num_bytes = len(in_bits)//8 #there should be no remainder
    out = [in_bits[(i*8): (i+1)*8] for i in range(num_bytes)]
    if (len(in_bits) % 8 != 0):
        out.append(in_bits[num_bytes*8:].zfill(8))
    return out

#message here should be a list of bytes, r and s are numbers
def poly(message, r, s):
    a = 0
    p = (2**130) - 5
    #print(p)
    msg = split_msg(message)
    for chunk in msg:
        #print("here")
        #print(byt_to_hex(chunk[::-1]))
        num_msg = bytes_to_number((chunk + ["00000001"])[::-1])
        #print(byt_to_hex(number_to_bytes(num_msg)))
        a += num_msg
        #print(byt_to_hex(number_to_bytes(a)))
        a *= r
        #print(byt_to_hex(number_to_bytes(a)))
        a = a % p
        #print(byt_to_hex(number_to_bytes(a)))
    a += s

    return number_to_bytes(a)

def main(): 
    #rs_hex_string = input("rs")
    args = list(sys.argv)[1:]
    if (len(args) != 3):
        print("Format : 32-byte key, name of file, 16-byte tag")

    #rs_hex_string = "85d6be7857556d337f4452fe42d506a80103808afb0db2fd4abff6af4149f51b"
    rs_hex_string = args[0]
    rs_hex_list = [rs_hex_string[(i*2): (i*2)+2] for i in range(32)]
    rs = hex_to_byt(rs_hex_list)
    r, s = read_rs(rs)
    #print(byt_to_hex(number_to_bytes(r)))
    #print(byt_to_hex(number_to_bytes(s)))
    #msg = read_file_byt("msg.txt")
    msg = read_file_byt(args[1])
    #print(byt_to_hex(msg))
    #print(msg)
    tag = poly(msg, r, s)
    tag = "".join(byt_to_hex(tag)[::-1][:16])
    if (tag == args[2]):
        print("ACCPET")
    else:
        print("REJECT")
    return
if __name__ == "__main__":
    main()
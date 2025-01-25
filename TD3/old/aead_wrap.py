#!/usr/bin/env python3
import sys
import chacha20
import poly1305_gen

#reads file as bits, then returns a list of bytes (file type doesn't matter it reads as binary)
def read_file_byt(filename):
    f = open(filename, "rb")
    content = f.read()
    f.close()
    out = []
    for x in content:
        binval = format(x, "b")
        while (len(binval) < 8):
            binval = "0" + binval
        out.append(binval)
    return out

#hex to bytes
def hex_to_byt(hex_list):
    byt_list = []
    for x in hex_list:
        byt_store = bin(int(x, 16))[2:].zfill(8)
        byt_list.append(byt_store)
    return byt_list

def main():
    args = list(sys.argv)[1:]
    if (len(args) != 5):
        print("Format : keyfile, nonce, adfile, plaintext file, cipher file (output)")
        return

    out = []
    key = read_file_byt(args[0])
    ad_in = read_file_byt(args[2])
    ad = [i for i in ad_in]
    while (len(ad) % 16 != 0):
        ad.append("00000000")
    msg = read_file_byt(args[3])

    b = 0
    #iv_in = "40 41 42 43 44 45 46 47"
    #iv = hex_to_byt(iv_in.split(" "))
    #fixed_in = "07 00 00 00"
    #fixed = hex_to_byt(fixed_in.split(" "))
    #nonce = fixed + iv
    nonce = hex_to_byt([args[1][i*2 : (i+1) * 2] for i in range(12)]) #should be 12 bytes
    #print(nonce)

    cha_state = chacha20.chacha20(key, b, nonce)
    cha_state_hex = []
    for value in cha_state:
        hex_val = hex(value)[2:].zfill(8)
        hex_list = [hex_val[i*2: (i+1)*2] for i in range(4)][::-1]
        cha_state_hex += hex_list
        poly_key_hex = cha_state_hex[:32]
    poly_key_bin = [bin(int(value, 16))[2:].zfill(8) for value in poly_key_hex]
    r, s = poly1305_gen.read_rs(poly_key_bin)
    #print(poly1305_gen.byt_to_hex(poly1305_gen.number_to_bytes(r)))
    #print(poly1305_gen.byt_to_hex(poly1305_gen.number_to_bytes(s)))

    #tagging the "header"
    '''
    a = 0
    p = (2**130) - 5
    a += poly1305_gen.bytes_to_number((ad + ["00000001"])[::-1])
    a *= r 
    a = a % p
    '''
    out += [hex(int(value, 2))[2:].zfill(2) for value in ad]

    for i in range(len(msg)//64 + 1):
        #chacha20.print_state(cha_state) 
        cha_state = chacha20.chacha20(key, b + i + 1, nonce)
        cha_state_hex = []
        for value in cha_state:
            hex_val = hex(value)[2:].zfill(8)
            hex_list = [hex_val[i*2: (i+1)*2] for i in range(4)][::-1]
            cha_state_hex += hex_list
        
        if ((i+1)*64 > len(msg)):
            msg_block = [hex(int(value, 2))[2:].zfill(2) for value in msg[i*64:]]
        else:
            msg_block = [hex(int(value, 2))[2:].zfill(2) for value in msg[i*64:(i+1)*64]]

        cipher = [chacha20.xor(int(msg_block[i],16), int(cha_state_hex[i],16)) for i in range(len(msg_block))]
        while (len(cipher) % 16 != 0):
            cipher.append(0) 
        #the cipher is 64bytes longs
        out += [hex(value)[2:].zfill(2) for value in cipher]
        ''' 
        cipher_no = [bin(value)[2:].zfill(8) for value in cipher]
        cipher_split = [cipher_no[i*16:(i+1)*16] for i in range(4)] #split into 16 bytes chunks
        for chunk in cipher_split:
            a += poly1305_gen.bytes_to_number((chunk + ["00000001"])[::-1])
            a *= r
            a = a % p
        '''

    #add on the length of ad and ciphertext and modify tag
    len_bytes_ad = hex(len(ad_in))[2:].zfill(16)
    len_bytes_cipher = hex(len(msg))[2:].zfill(16)
    tail = [len_bytes_ad[i*2: (i+1)*2] for i in range(8)][::-1]
    tail += [len_bytes_cipher[i*2: (i+1)*2] for i in range(8)][::-1]
    out += tail
    #print(bytearray([int(value, 16) for value in out]))

    '''
    a += poly1305_gen.bytes_to_number((hex_to_byt(tail) + ["00000001"])[::-1])
    a *= r
    a = a % p
    '''

    tag = poly1305_gen.poly(hex_to_byt(out), r, s)[::-1][:16]
    #print("".join(out))
    file_to_save = open(args[4], "wb")
    file_to_save.write(bytes(bytearray([int(value, 16) for value in out])))
    file_to_save.close()
    print("".join([hex(int(value, 2))[2:].zfill(2) for value in tag]))


if __name__ == "__main__":
    main()


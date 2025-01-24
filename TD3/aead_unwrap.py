#!/usr/bin/env python3
import sys
import chacha20
import poly1305_check

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
        print("Format : keyfile, nonce, adfile, cipher file, tag")
        return
    
    key = read_file_byt(args[0])
    nonce = hex_to_byt([args[1][i*2 : (i+1) * 2] for i in range(12)]) #should be 12 bytes
    ad_in = read_file_byt(args[2])
    ad = [i for i in ad_in]
    while (len(ad) % 16 != 0):
        ad.append("00000000")
    cipher = read_file_byt(args[3])
    b = 0

    cha_state = chacha20.chacha20(key, b, nonce)
    cha_state_hex = []
    for value in cha_state:
        hex_val = hex(value)[2:].zfill(8)
        hex_list = [hex_val[i*2: (i+1)*2] for i in range(4)][::-1]
        cha_state_hex += hex_list
        poly_key_hex = cha_state_hex[:32]
    poly_key_bin = [bin(int(value, 16))[2:].zfill(8) for value in poly_key_hex]
    r, s = poly1305_check.read_rs(poly_key_bin)
    
    tag = poly1305_check.poly(cipher, r, s)
    tag = "".join(poly1305_check.byt_to_hex(tag)[::-1][:16])
    if (tag != args[4]):
        print(tag)
        print("REJECT")
    else:
        lengths = cipher[-16:]
        aad_length = lengths[:8][::-1]
        cipher_text_lenght = lengths[8:][::-1]
        aad_length = int("".join(aad_length), 2)
        cipher_text_lenght = int("".join(cipher_text_lenght), 2)

        if (aad_length % 16 != 0):
            aad_length += 16 - (aad_length % 16)

        cipher = cipher[aad_length:]
        cipher = cipher[:cipher_text_lenght]
        #print([hex(int(value,2))[2:].zfill(2) for value in cipher])

        to_xor = []
        for i in range(len(cipher)//64 + 1): 
            state = chacha20.chacha20(key, b + i + 1, nonce)
            #print_state(state)
            for entry in state:
                hex_val = hex(entry)[2:]
                if (len(hex_val) < 8):
                    hex_val = hex_val.zfill(8) 
                hex_list = [hex_val[i*2: (i+1)*2] for i in range(4)][::-1]
                to_xor += hex_list

        msg = [hex(int(value, 2))[2:].zfill(2) for value in cipher]

        out = [chacha20.xor(int(msg[i],16), int(to_xor[i],16)) for i in range(len(msg))]
        out = bytes(bytearray(out))
        out = out.decode("utf-8")
        print(out)

        #file_to_save = open(args[5], "wb")
        #file_to_save.write(bytes(bytearray(out)))
        #file_to_save.close()

if __name__ == "__main__":
    main()



#!/usr/bin/env python3
import sys
import chacha20
import poly1305_check

def main():
    args = list(sys.argv)[1:]
    if (len(args) != 5):
        print("Format : keyfile, nonce, adfile, cipher file, tag")
        return
    
    key = chacha20.read_file_byt(args[0])
    nonce = chacha20.hexs_to_byts([args[1][i*2 : (i+1) * 2] for i in range(12)]) #should be 12 bytes
    ad = chacha20.read_file_byt(args[2])
    ad_len = len(ad)
    while (len(ad) % 16 != 0):
        ad.append("00000000")

    cipher = chacha20.read_file_byt(args[3])
    b = 0

    cha_state = chacha20.gen_state(key, b, nonce)
    poly_key = []
    for bit32 in cha_state:
        poly_key += [bit32[i*8: (i+1)*8] for i in range(4)][::-1]
    r, s = poly1305_check.read_rs(poly_key[:32])
    
    tag = poly1305_check.poly(cipher, r, s)
    tag = "".join(poly1305_check.byt_to_hex(tag)[::-1][:16])
    if (tag != args[4]):
        #print(tag)
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

        out = []
        for i in range(len(cipher)//64 + 1): 
            state = chacha20.gen_state(key, b + i + 1, nonce)
            if (i+1)*64 > len(cipher):
                cipher_part = cipher[i*64:]
            else:
                cipher_part = cipher[i*64: (i+1)*64]
            out += chacha20.encrypt(cipher_part, state)  

        out = bytes(bytearray(out))
        out = out.decode("utf-8")
        print(out)

        #file_to_save = open(args[5], "wb")
        #file_to_save.write(bytes(bytearray(out)))
        #file_to_save.close()

if __name__ == "__main__":
    main()



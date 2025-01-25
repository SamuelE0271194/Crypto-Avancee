#!/usr/bin/env python3
import sys
import chacha20
import poly1305_gen

def main():
    args = list(sys.argv)[1:]
    if (len(args) != 5):
        print("Format : keyfile, nonce, adfile, plaintext file, cipher file (output)")
        return

    out = []
    key = chacha20.read_file_byt(args[0])
    nonce = chacha20.hexs_to_byts([args[1][i*2 : (i+1) * 2] for i in range(12)]) #should be 12 bytes
    ad = chacha20.read_file_byt(args[2])
    ad_len = len(ad)
    while (len(ad) % 16 != 0):
        ad.append("00000000")

    msg = chacha20.read_file_byt(args[3])

    b = 0

    #this in in binary
    cha_state = chacha20.gen_state(key, b, nonce)
    poly_key = []
    for bit32 in cha_state:
        poly_key += [bit32[i*8: (i+1)*8] for i in range(4)][::-1]
    r, s = poly1305_gen.read_rs(poly_key[:32])

    out = []
    #tagging the "header"
    a = 0
    p = (2**130) - 5
    a += poly1305_gen.bytes_to_number((ad + ["00000001"])[::-1])
    a *= r 
    a %= p

    out += ad

    for i in range(len(msg)//64 + 1):
        cha_state = chacha20.gen_state(key, b + i + 1, nonce)
        if ((i+1)*64 > len(msg)):
            msg_part = msg[i*64:]
        else:
            msg_part = msg[i*64: (i+1)*64]

        to_add = chacha20.encrypt(msg_part, cha_state)
        while (len(to_add) < 64):
            to_add.append(0)
        to_add = [bin(x)[2:].zfill(8) for x in to_add]
        for j in range(4): #split to_add into 4 (16-bits)chunks
            to_tag = to_add[j*16: (j+1)*16]
            a += poly1305_gen.bytes_to_number((to_tag + ["00000001"])[::-1])
            a *= r
            a %= p
        out += to_add

    len_bytes_ad = bin(ad_len)[2:].zfill(64)
    len_bytes_cipher = bin(len(msg))[2:].zfill(64)

    tail = [len_bytes_ad[i*8: (i+1)*8] for i in range(8)][::-1]
    tail += [len_bytes_cipher[i*8: (i+1)*8] for i in range(8)][::-1]
    a += poly1305_gen.bytes_to_number((tail + ["00000001"])[::-1])
    a *= r
    a %= p
    out += tail

    tag = a + s

    tag = poly1305_gen.number_to_bytes(tag)
    tag = chacha20.byts_to_hexs(tag)[::-1][:16]
    file_to_save = open(args[4], "wb")
    file_to_save.write(bytes(bytearray([int(value, 2) for value in out])))
    file_to_save.close()
    print("".join(tag))

if __name__ == "__main__":
    main()


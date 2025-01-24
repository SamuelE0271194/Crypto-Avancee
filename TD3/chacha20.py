#!/usr/bin/env python3
import sys

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

def print_state(state):
    out = [hex(entry) for entry in state]
    for i in range(4):
        temp = out[i*4: (i+1)*4]
        temp = [value[2:].zfill(8) for value in temp]
        print(temp)

#these all take integers (2**32 max)
def add(a, b):
    return ((a + b) % (2**32))

def xor(a, b):
    return a ^ b

def rotate(a, rounds):
    a_bin = bin(a)[2:].zfill(32)
    a_bin = a_bin[rounds:] + a_bin[:rounds]
    return int(a_bin, 2)


def quarterRound(state, i, j, k, l):
    a = state[i]
    b = state[j]
    c = state[k]
    d = state[l]

    a = add(a, b)
    d = xor(d, a)
    d = rotate(d, 16)
    
    c = add(c, d)
    b = xor(b, c)
    b = rotate(b, 12)

    a = add(a, b)
    d = xor(d, a)
    d = rotate(d, 8)

    c = add(c, d)
    b = xor(b, c)
    b = rotate(b, 7)

    state[i] = a
    state[j] = b
    state[k] = c
    state[l] = d

def chachaRounds(state):

    for i in range(10): #10 rounds of col and diag
        
        quarterRound(state, 0, 4, 8, 12)
        quarterRound(state, 1, 5, 9, 13)
        quarterRound(state, 2, 6, 10, 14)
        quarterRound(state, 3, 7, 11, 15)

        quarterRound(state, 0, 5, 10, 15)
        quarterRound(state, 1, 6, 11, 12)
        quarterRound(state, 2, 7, 8, 13)
        quarterRound(state, 3, 4, 9, 14)

    return state

#k is a list of 64 bytes (this is in the "inverted form")
#b is an integer!! (32 bits)
#n is a list of 3, 32-bit integers (this is in the "inverted form")
def chacha20(k, b, n):
    c0 = int(0x61707865)
    c1 = int(0x3320646e)
    c2 = int(0x79622d32)
    c3 = int(0x6b206574)

    state = [c0, c1, c2, c3]
    for i in range(8):
        k_i = "".join(k[i*4 : (i+1) * 4][::-1])
        state.append(int(k_i, 2))
    state.append(b)
    for i in range(3):
        n_i = "".join(n[i*4: (i+1)*4][::-1])
        state.append(int(n_i, 2))
    
    old_state = [entry for entry in state]
    chachaRounds(state)
    state = [add(state[i], old_state[i]) for i in range(16)]
    #print_state(state)
    #print("~~~~~~~~~~~~")
    return state

def main():
    args = list(sys.argv)[1:]
    if (len(args) != 4):
        print("Format : keyfile, nonce, input text, output text")
        return

    msg = read_file_byt(args[2])
    key = read_file_byt(args[0])
    nonce = hex_to_byt([args[1][i*2 : (i+1) * 2] for i in range(12)]) #should be 12 bytes
    b = 1
    #print(nonce)
    to_xor = []
    for i in range(len(msg)//64 + 1): 
        state = chacha20(key, b+i, nonce)
        #print_state(state)
        for entry in state:
            hex_val = hex(entry)[2:]
            if (len(hex_val) < 8):
                hex_val = hex_val.zfill(8) 
            hex_list = [hex_val[i*2: (i+1)*2] for i in range(4)][::-1]
            to_xor += hex_list

    msg = [hex(int(value, 2))[2:].zfill(2) for value in msg]

    out = [xor(int(msg[i],16), int(to_xor[i],16)) for i in range(len(msg))]
    #temp = [hex(value).zfill(2)[2:].zfill(2) for value in out]
    #print(temp)
    #print(bytes(bytearray(out)))

    file_to_save = open(args[3], "wb")
    file_to_save.write(bytes(bytearray(out)))
    file_to_save.close()
    return

if __name__ == "__main__":
    main()

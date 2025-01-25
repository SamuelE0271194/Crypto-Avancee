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

#Some conversion tools
def hex_to_byt(hex_val):
    byt_val = bin(int(hex_val, 16))[2:].zfill(8)
    return byt_val

def hexs_to_byts(hex_list):
    byt_list = list(map(lambda x: hex_to_byt(x), hex_list))
    return byt_list

def byt_to_hex(byt_val):
    hex_val = hex(int(byt_val, 2))[2:].zfill(2)
    return hex_val

def byts_to_hexs(byt_list):
    hex_list = list(map(lambda x: byt_to_hex(x), byt_list))
    return hex_list

#view the state in a table form
def print_state(state):
    for i in range(4):
        print(state[i*4: (i+1)*4])

#these all take integers (2**32 max)
def add(a, b):
    return ((a + b) % (2**32))

def xor(a, b):
    return a ^ b

def rotate(a, rounds):
    a_bin = bin(a)[2:].zfill(32)
    a_bin = a_bin[rounds:] + a_bin[:rounds]
    return int(a_bin, 2)

#quarter round
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

#20 rounds
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

#generates the initial state without chacha
#k is a list of 64 bytes (this is in the "inverted form")
#b is an integer!! (32 bits)
#n is a list of 3, 32-bit integers (this is in the "inverted form")
def gen_state(k, b, n):
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
    
    state = [bin(x)[2:].zfill(32) for x in state] 
    return state #output is in bytes (32bits)

#the msg and states should be a list of bytes
# the state is in the table form, ie the entries need to be filpped (state is in bytes)
def encrypt(msg, state):
    to_xor = [x for x in state]
    temp = []
    
    for bit32 in to_xor:
        temp += [bit32[i*8: (i+1)*8] for i in range(4)][::-1]

    out = [] 
    for i in range(len(msg)):
        out.append(xor(int(msg[i], 2), int(temp[i], 2)))
    
    return out

def main():
    args = list(sys.argv)[1:]
    if (len(args) != 4):
        print("Format : keyfile, nonce, input text, output text")
        return

    msg = read_file_byt(args[2])
    key = read_file_byt(args[0])
    nonce = hexs_to_byts([args[1][i*2 : (i+1) * 2] for i in range(12)]) #should be 12 bytes
    b = 1

    out = [] 
    for i in range(len(msg)//64 + 1): 
        state = gen_state(key, b+i, nonce)
        if (i+1)*64 > len(msg):
            msg_part = msg[i*64:]
        else:
            msg_part = msg[i*64: (i+1)*64]

        #this is the main part 
        out += encrypt(msg_part, state)

    #print(bytearray(out))
    file_to_save = open(args[3], "wb")
    file_to_save.write(bytes(bytearray(out)))
    file_to_save.close()
    return

if __name__ == "__main__":
    main()
